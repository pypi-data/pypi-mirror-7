#!/usr/bin/env python
"""
Top-level interface to Grid functionality.
"""
# Copyright (C) 2009-2012 GC3, University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
__docformat__ = 'reStructuredText'
__version__ = '2.1.4 version (SVN $Revision: 3953 $)'
__date__ = '$Date$'


from fnmatch import fnmatch
import os
import posix
import re
import sys
import time
import ConfigParser
import tempfile
import warnings
warnings.simplefilter("ignore")

from gc3libs.compat._collections import defaultdict

import gc3libs
import gc3libs.debug
from gc3libs import Application, Run, Task
from gc3libs.backends.sge import SgeLrms
from gc3libs.backends.pbs import PbsLrms
from gc3libs.backends.lsf import LsfLrms
from gc3libs.backends.shellcmd import ShellcmdLrms
from gc3libs.authentication import Auth
import gc3libs.exceptions
import gc3libs.utils as utils


class Core:
    """Core operations: submit, update state, retrieve (a
snapshot of) output, cancel job.

Core operations are *blocking*, i.e., they return only after the
operation has successfully completed, or an error has been detected.

Operations are always performed by a `Core` object.
`Core` implements an overlay Grid on the resources
specified in the configuration file.
    """
    def __init__(self, cfg):
        # init auths
        self.auto_enable_auth = cfg.auto_enable_auth

        # init backends
        self._lrms = cfg.make_resources()
        if len(self._lrms) == 0:
            raise gc3libs.exceptions.NoResources(
                "No resources given to initialize `gc3libs.core.Core` object!")


    def get_backend(self, name):
        try:
            return self._lrms[name]
        except KeyError:
            raise gc3libs.exceptions.InvalidResourceName(
                "Cannot find computational resource '%s'" %
                name)


    def select_resource(self, match):
        """
        Alter the configured list of resources, and retain only those
        that satisfy predicate `match`.

        Argument `match` can be:

          - either a function (or a generic callable) that is passed
            each `Resource` object in turn, and should return a
            boolean indicating whether the resources should be kept
            (`True`) or not (`False`);

          - or it can be a string: only resources whose name matches
            (wildcards ``*`` and ``?`` are allowed) are retained.
        """
        for lrms in self._lrms.itervalues():
            try:
                if not match(lrms):
                    lrms.enabled = False
            except:
                if not fnmatch(lrms.name, match):
                    lrms.enabled = False
        return len(self._lrms)


    def free(self, app, **extra_args):
        """
        Free up any remote resources used for the execution of `app`.
        In particular, this should delete any remote directories and
        files.

        It is an error to call this method if `app.execution.state` is
        anything other than `TERMINATED`: an `InvalidOperation` exception
        will be raised in this case.

        :raise: `gc3libs.exceptions.InvalidOperation` if `app.execution.state`
                differs from `Run.State.TERMINATED`.
        """
        assert isinstance(app, Task), \
            "Core.free: passed an `app` argument which is not a `Task` instance."
        if isinstance(app, Application):
            return self.__free_application(app, **extra_args)
        else:
            # must be a `Task` instance
            return self.__free_task(app, **extra_args)

    def __free_application(self, app, **extra_args):
        """Implementation of `free` on `Application` objects."""
        if app.execution.state not in [ Run.State.TERMINATING, Run.State.TERMINATED ]:
            raise gc3libs.exceptions.InvalidOperation(
                "Attempting to free resources of job '%s',"
                " which is in non-terminal state." % app)

        auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)

        if hasattr(app.execution, 'resource_name'):
            lrms =  self.get_backend(app.execution.resource_name)
            lrms.free(app)
        else:
            gc3libs.log.debug(
                "Core.__free_application(): Application `%s` does not have an "
                "`execution.resource_name` attribute. Assuming it has been "
                "aborted before submission." % str(app))

    def __free_task(self, task, **extra_args):
        """Implementation of `free` on generic `Task` objects."""
        return task.free(**extra_args)


    def submit(self, app, resubmit=False, **extra_args):
        """
        Submit a job running an instance of the given `app`.  Upon
        successful submission, call the `submitted` method on the
        `app` object.

        At the beginning of the submission process, the
        `app.execution` state is reset to ``NEW``; if submission is
        successfull, the task will be in ``SUBMITTED`` or ``RUNNING``
        state when this call returns.

        :raise: `gc3libs.exceptions.InputFileError` if an input file
                does not exist or cannot otherwise be read.
        """
        assert isinstance(app, Task), \
            "Core.submit: passed an `app` argument which is not a `Task` instance."
        if isinstance(app, Application):
            return self.__submit_application(app, resubmit, **extra_args)
        else:
            # must be a `Task` instance
            return self.__submit_task(app, resubmit, **extra_args)

    def __submit_application(self, app, resubmit, **extra_args):
        """Implementation of `submit` on `Application` objects."""

        gc3libs.log.debug("Submitting %s ..." % str(app))

        auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)

        job = app.execution
        if resubmit:
            job.state = Run.State.NEW
        elif job.state != Run.State.NEW:
            return

        lrms_list = filter(lambda x: x.enabled, self._lrms.itervalues())
        if len(lrms_list) == 0:
            raise gc3libs.exceptions.NoResources(
                "Could not initialize any computational resource"
                " - please check log and configuration file.")

        gc3libs.log.debug('Performing brokering ...')
        # decide which resource to use
        # (Resource)[] = (Scheduler).PerformBrokering((Resource)[],(Application))
        _selected_lrms_list = app.compatible_resources(lrms_list)
        gc3libs.log.debug('Application scheduler returned %d matching resources',
                           len(_selected_lrms_list))
        if 0 == len(_selected_lrms_list):
            raise gc3libs.exceptions.NoResources(
                "No available resource can accomodate the application requirements")

        if len(_selected_lrms_list) <= 1:
            # shortcut: no brokering to do, just use what we've got
            updated_resources = _selected_lrms_list
        else:
            # update status of selected resources
            updated_resources = []
            for r in _selected_lrms_list:
                try:
                    # in-place update of resource status
                    gc3libs.log.debug(
                        "Trying to update status of resource '%s' ..."
                        % r.name)
                    r.get_resource_status()
                    updated_resources.append(r)
                except Exception, x:
                    # ignore errors in update, assume resource has a problem
                    # and just drop it
                    gc3libs.log.error("Cannot update status of resource '%s', dropping it."
                                      " See log file for details."
                                      % r.name)
                    gc3libs.log.debug("Got error from get_resource_status(): %s: %s",
                                      x.__class__.__name__, str(x), exc_info=True)

        # sort resources according to Application's preferences
        _selected_lrms_list = app.rank_resources(updated_resources)
        if len(_selected_lrms_list) == 0:
            raise gc3libs.exceptions.LRMSSubmitError(
                "No computational resources left after brokering."
                " Aborting submission of job '%s'" % app)

        exs = [ ]
        # Scheduler.do_brokering returns a sorted list of valid lrms
        for lrms in _selected_lrms_list:
            gc3libs.log.debug("Attempting submission to resource '%s'..."
                              % lrms.name)
            try:
                job.timestamp[Run.State.NEW] = time.time()
                job.info = ("Submitting to '%s' at %s"
                        % (lrms.name,
                           time.ctime(job.timestamp[Run.State.NEW])))
                lrms.submit_job(app)
            except gc3libs.exceptions.LRMSSkipSubmissionToNextIteration, ex:
                gc3libs.log.info(
                    "Submission of job %s delayed" % app)
                exs.append(ex)
                break
            except Exception, ex:
                gc3libs.log.info(
                    "Error in submitting job to resource '%s': %s: %s",
                    lrms.name, ex.__class__.__name__, str(ex),
                    exc_info=True)
                exs.append(ex)
                continue
            gc3libs.log.info("Successfully submitted %s to: %s",
                             str(app), lrms.name)
            job.state = Run.State.SUBMITTED
            job.resource_name = lrms.name
            job.info = ("Submitted to '%s' at %s"
                        % (job.resource_name,
                           time.ctime(job.timestamp[Run.State.SUBMITTED])))
            app.changed = True
            app.submitted()
            # job submitted; return to caller
            return
        # if wet get here, all submissions have failed; call the
        # appropriate handler method if defined
        ex = app.submit_error(exs)
        if isinstance(ex, Exception):
            app.execution.info = ("Submission failed: %s" % str(ex))
            raise ex
        else:
            return

    def __submit_task(self, task, resubmit, **extra_args):
        """Implementation of `submit` on generic `Task` objects."""
        extra_args.setdefault('auto_enable_auth', self.auto_enable_auth)
        task.submit(resubmit, **extra_args)


    def update_job_state(self, *apps, **extra_args):
        """
        Update state of all applications passed in as arguments.

        If keyword argument `update_on_error` is `False` (default),
        then application execution state is not changed in case a
        backend error happens; it is changed to `UNKNOWN` otherwise.

        Note that if state of a job changes, the `Run.state` calls the
        appropriate handler method on the application/task object.

        :raise: `gc3libs.exceptions.InvalidArgument` in case one of
                the passed `Application` or `Task` objects is
                invalid. This can stop updating the state of other
                objects in the argument list.

        :raise: `gc3libs.exceptions.ConfigurationError` if the
                configuration of this `Core` object is invalid or
                otherwise inconsistent (e.g., a resource references a
                non-existing auth section).

        """
        self.__update_application((app for app in apps if isinstance(app, Application)), **extra_args)
        self.__update_task((app for app in apps if not isinstance(app, Application)), **extra_args)

    def __update_application(self, apps, **extra_args):
        """Implementation of `update_job_state` on `Application` objects."""
        update_on_error = extra_args.get('update_on_error', False)
        auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)

        for app in apps:
            state = app.execution.state
            old_state = state
            gc3libs.log.debug("About to update state of application: %s (currently: %s)", app, state)
            try:
                if state not in [ Run.State.NEW,
                                  Run.State.TERMINATING,
                                  Run.State.TERMINATED,
                                  ]:
                    lrms = self.get_backend(app.execution.resource_name)
                    try:
                        state = lrms.update_job_state(app)
                    except Exception, ex:
                        gc3libs.log.debug(
                            "Error getting status of application '%s': %s: %s",
                            app, ex.__class__.__name__, str(ex), exc_info=True)
                        state = Run.State.UNKNOWN
                        # run error handler if defined
                        ex = app.update_job_state_error(ex)
                        if isinstance(ex, Exception):
                            raise ex
                    if state != old_state:
                        app.changed = True
                        # set log information accordingly
                        if (app.execution.state == Run.State.TERMINATING
                            and app.execution.returncode is not None
                            and app.execution.returncode != 0):
                            # there was some error, try to explain
                            app.execution.info = ("Execution failed on resource: %s" % app.execution.resource_name)
                            signal = app.execution.signal
                            if signal in Run.Signals:
                                app.execution.info = ("Abnormal termination: %s" % signal)
                            else:
                                if os.WIFSIGNALED(app.execution.returncode):
                                    app.execution.info = ("Remote job terminated by signal %d" % signal)
                                else:
                                    app.execution.info = ("Remote job exited with code %d"
                                                          % app.execution.exitcode)

                    if state != Run.State.UNKNOWN or update_on_error:
                        app.execution.state = state

            except (gc3libs.exceptions.InvalidArgument,
                    gc3libs.exceptions.ConfigurationError,
                    gc3libs.exceptions.UnrecoverableAuthError,
                    gc3libs.exceptions.FatalError):
                # Unrecoverable; no sense in continuing --
                # pass immediately on to client code and let
                # it handle this...
                raise

            except gc3libs.exceptions.UnknownJob:
                # information about the job is lost, mark it as failed
                app.execution.returncode = (Run.Signals.Lost, -1)
                app.execution.state = Run.State.TERMINATED
                app.changed = True
                continue


            except gc3libs.exceptions.InvalidResourceName, irn:
                # could be the corresponding LRMS has been removed because of an unrecoverable error
                # mark application as state UNKNOWN
                gc3libs.log.warning("Failed while retrieving resource %s from core.Detailed Error message: %s" % (app.execution.resource_name, str(irn)))
                continue

            # XXX: Re-enabled the catch-all clause otherwise the loop stops at the first erroneous iteration
            except Exception, ex:
                if 'GC3PIE_NO_CATCH_ERRORS' in os.environ:
                    # propagate generic exceptions for debugging purposes
                    raise
                else:
                    gc3libs.log.warning("Ignored error in Core.update_job_state(): %s", str(ex))
                    # print again with traceback at a higher log level
                    gc3libs.log.debug("Ignored error in Core.update_job_state(): %s: %s",
                                      ex.__class__.__name__, str(ex), exc_info=True)
                    continue

    def __update_task(self, tasks, **extra_args):
        """Implementation of `update_job_state` on generic `Task` objects."""
        for task in tasks:
            assert isinstance(task, Task), \
                   "Core.update_job_state: passed an argument which is not a `Task` instance."
            task.update_state()


    def fetch_output(self, app, download_dir=None, overwrite=False, **extra_args):
        """
        Retrieve output into local directory `app.output_dir`;
        optional argument `download_dir` overrides this.

        The download directory is created if it does not exist.  If it
        already exists, and the optional argument `overwrite` is
        `False` (default), it is renamed with a `.NUMBER` suffix and a
        new empty one is created in its place.  Otherwise, if
        'overwrite` is `True`, files are downloaded over the ones
        already present.

        If the task is in TERMINATING state, the state is changed to
        `TERMINATED`, attribute `output_dir`:attr: is set to the
        absolute path to the directory where files were downloaded,
        and the `terminated` transition method is called on the `app`
        object.

        Task output cannot be retrieved when `app.execution` is in one
        of the states `NEW` or `SUBMITTED`; an
        `OutputNotAvailableError` exception is thrown in these cases.

        :raise: `gc3libs.exceptions.OutputNotAvailableError` if no
                output can be fetched from the remote job (e.g., the
                Application/Task object is in `NEW` or `SUBMITTED`
                state, indicating the remote job has not started
                running).
        """
        assert isinstance(app, Task), \
            "Core.fetch_output: passed an `app` argument which is not a `Task` instance."
        if isinstance(app, Application):
            self.__fetch_output_application(app, download_dir, overwrite, **extra_args)
        else:
            # generic `Task` object
            self.__fetch_output_task(app, download_dir, overwrite, **extra_args)

    def __fetch_output_application(self, app, download_dir, overwrite, **extra_args):
        """Implementation of `fetch_output` on `Application` objects."""
        job = app.execution
        if job.state in [ Run.State.NEW, Run.State.SUBMITTED ]:
            raise gc3libs.exceptions.OutputNotAvailableError(
                "Output not available: '%s' currently in state '%s'"
                % (app, app.execution.state))

        auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)

        # determine download dir
        download_dir = app._get_download_dir(download_dir)

        # Prepare/Clean download dir
        try:
            if overwrite:
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
            else:
                utils.mkdir_with_backup(download_dir)
        except Exception, ex:
            gc3libs.log.error("Failed creating download directory '%s': %s: %s",
                              download_dir, ex.__class__.__name__, str(ex))
            raise

        # download job output
        try:
            lrms = self.get_backend(job.resource_name)
            # self.auths.get(lrms.auth)
            lrms.get_results(app, download_dir)
            # clear previous data staging errors
            if job.signal == Run.Signals.DataStagingFailure:
                job.signal = 0
        except gc3libs.exceptions.InvalidResourceName, ex:
            gc3libs.log.warning(
                "Failed retrieving resource %s from core."
                " Detailed Error message: %s" % (app.execution.resource_name, str(ex)))
            ex = app.fetch_output_error(ex)
            if isinstance(ex, Exception):
                job.info = ("No output could be retrieved: %s" % str(ex))
                raise ex
            else:
                return
        except gc3libs.exceptions.RecoverableDataStagingError, rex:
            job.info = ("Temporary failure when retrieving results: %s."
                        " Ignoring error, try again." % str(rex))
            return
        except gc3libs.exceptions.UnrecoverableDataStagingError, ex:
            job.signal = Run.Signals.DataStagingFailure
            ex = app.fetch_output_error(ex)
            if isinstance(ex, Exception):
                job.info = ("No output could be retrieved: %s" % str(ex))
                raise ex
        except Exception, ex:
            ex = app.fetch_output_error(ex)
            if isinstance(ex, Exception):
                raise ex

        # successfully downloaded results
        gc3libs.log.debug("Downloaded output of '%s' (which is in state %s)"
                          % (str(app), job.state))

        app.output_dir = os.path.abspath(download_dir)
        app.changed = True

        if job.state == Run.State.TERMINATING:
            gc3libs.log.debug("Final output of '%s' retrieved" % str(app))
        return Task.fetch_output(app, download_dir)


    def __fetch_output_task(self, task, download_dir, overwrite, **extra_args):
        """Implementation of `fetch_output` on generic `Task` objects."""
        return task.fetch_output(download_dir, overwrite, **extra_args)


    def get_resources(self, **extra_args):
        """
        Return list of resources configured into this `Core` instance.
        """
        return [ lrms for lrms in self._lrms.itervalues() ]


    def kill(self, app, **extra_args):
        """
        Terminate a job.

        Terminating a job in RUNNING, SUBMITTED, or STOPPED state
        entails canceling the job with the remote execution system;
        terminating a job in the NEW or TERMINATED state is a no-op.
        """
        assert isinstance(app, Task), \
            "Core.kill: passed an `app` argument which is not a `Task` instance."
        if isinstance(app, Application):
            self.__kill_application(app, **extra_args)
        else:
            self.__kill_task(app, **extra_args)

    def __kill_application(self, app, **extra_args):
        """Implementation of `kill` on `Application` objects."""
        job = app.execution
        auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)
        try:
            lrms = self.get_backend(job.resource_name)
            lrms.cancel_job(app)
        except AttributeError:
            # A job in state NEW does not have a `resource_name`
            # attribute.
            if job.state != Run.State.NEW:
                raise
        except gc3libs.exceptions.InvalidResourceName, irn:
            gc3libs.log.warning("Failed while retrieving resource %s from core.Detailed Error message: %s" % (app.execution.resource_name, str(irn)))
        gc3libs.log.debug("Setting job '%s' status to TERMINATED"
                          " and returncode to SIGCANCEL" % job)
        app.changed = True
        # setting the state runs the state-transition handlers,
        # which may raise an error -- ignore them, but log nonetheless
        try:
            job.state = Run.State.TERMINATED
        except Exception, ex:
            gc3libs.log.info("Ignoring error in state transition"
                             " since task is being killed: %s",
                             str(ex))
        job.signal = Run.Signals.Cancelled
        job.history.append("Cancelled")

    def __kill_task(self, task, **extra_args):
        extra_args.setdefault('auto_enable_auth', self.auto_enable_auth)
        task.kill(**extra_args)


    def peek(self, app, what='stdout', offset=0, size=None, **extra_args):
        """
        Download `size` bytes (at `offset` bytes from the start) from
        the remote job standard output or error stream, and write them
        into a local file.  Return file-like object from which the
        downloaded contents can be read.

        If `size` is `None` (default), then snarf all available
        contents of the remote stream from `offset` unto the end.

        The only allowed values for the `what` arguments are the
        strings `'stdout'` and `'stderr'`, indicating that the
        relevant section of the job's standard output resp. standard
        error should be downloaded.
        """
        assert isinstance(app, Task), \
            "Core.peek: passed an `app` argument which is not a `Task` instance."
        if isinstance(app, Application):
            return self.__peek_application(app, what, offset, size, **extra_args)
        else:
            return self.__peek_task(app, what, offset, size, **extra_args)

    def __peek_application(self, app, what, offset, size, **extra_args):
        """Implementation of `peek` on `Application` objects."""
        job = app.execution
        if what == 'stdout':
            remote_filename = job.stdout_filename
        elif what == 'stderr':
            remote_filename = job.stderr_filename
        else:
            raise Error("File name requested to `Core.peek` must be"
                        " 'stdout' or 'stderr', not '%s'" % what)

        # Check if local data available
        if job.state == Run.State.TERMINATED:
            # FIXME: local data could be stale!!
            filename = os.path.join(app.output_dir, remote_filename)
            local_file = open(filename, 'r')
        else:
            # Get authN
            auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)
            lrms = self.get_backend(job.resource_name)
            local_file = tempfile.NamedTemporaryFile(suffix='.tmp', prefix='gc3libs.')
            lrms.peek(app, remote_filename, local_file, offset, size)
            local_file.flush()
            local_file.seek(0)

        return local_file

    def __peek_task(self, task, what, offset, size, **extra_args):
        """Implementation of `peek` on generic `Task` objects."""
        return task.peek(what, offset, size, **extra_args)


    def update_resources(self, **extra_args):
        """
        Update the state of resources configured into this `Core` instance.

        Each resource object in the returned list will have its `updated` attribute
        set to `True` if the update operation succeeded, or `False` if it failed.
        """
        for lrms in self._lrms.itervalues():
            try:
                if not lrms.enabled:
                    continue
                auto_enable_auth = extra_args.get('auto_enable_auth', self.auto_enable_auth)
                resource = lrms.get_resource_status()
                resource.updated = True
            except Exception, ex:
                gc3libs.log.error("Got error while updating resource '%s': %s."
                                  % (lrms.name, str(ex)))
                lrms.updated = False


    def close(self):
        """
        Used to invoke explicitly the destructor on objects
        e.g. LRMS
        """
        for lrms in self._lrms.itervalues():
            lrms.close()


    ## compatibility with the `Engine` interface

    def add(self, task):
        """
        This method is here just to allow `Core` and `Engine` objects
        to be used interchangeably.  It's effectively a no-op, as it makes
        no sense in the synchronous/blocking semantics implemented by `Core`.
        """
        pass


    def remove(self, task):
        """
        This method is here just to allow `Core` and `Engine` objects
        to be used interchangeably.  It's effectively a no-op, as it makes
        no sense in the synchronous/blocking semantics implemented by `Core`.
        """
        pass


# Work around infinite recursion error when trying to compare
# `UserDict` instances which can contain each other.  We know
# that two identical tasks are the same object by
# construction, so let's use this to check.
def _contained(elt, lst):
    i = id(elt)
    for item in lst:
        if i == id(item):
            return True
    return False


class Engine(object):
    """
    Submit tasks in a collection, and update their state until a
    terminal state is reached. Specifically:

      * tasks in `NEW` state are submitted;

      * the state of tasks in `SUBMITTED`, `RUNNING` or `STOPPED` state is updated;

      * when a task reaches `TERMINATED` state, its output is downloaded.

    The behavior of `Engine` instances can be further customized by
    setting the following instance attributes:

      `can_submit`
        Boolean value: if `False`, no task will be submitted.

      `can_retrieve`
        Boolean value: if `False`, no output will ever be retrieved.

      `max_in_flight`
        If >0, limit the number of tasks in `SUBMITTED` or `RUNNING`
        state: if the number of tasks in `SUBMITTED`, `RUNNING` or
        `STOPPED` state is greater than `max_in_flight`, then no new
        submissions will be attempted.

      `max_submitted`
        If >0, limit the number of tasks in `SUBMITTED` state: if the
        number of tasks in `SUBMITTED`, `RUNNING` or `STOPPED` state is
        greater than `max_submitted`, then no new submissions will be
        attempted.

      `output_dir`
        Base directory for job output; if not `None`, each task's
        results will be downloaded in a subdirectory named after the
        task's `permanent_id`.

      `fetch_output_overwrites`
        Default value to pass as the `overwrite` argument to
        :meth:`Core.fetch_output` when retrieving results of a
        terminated task.

    Any of the above can also be set by passing a keyword argument to
    the constructor (assume ``g`` is a `Core`:class: instance)::

      | >>> e = Engine(g, can_submit=False)
      | >>> e.can_submit
      | False
    """


    def __init__(self, controller, tasks=list(), store=None,
                 can_submit=True, can_retrieve=True,
                 max_in_flight=0, max_submitted=0,
                 output_dir=None, fetch_output_overwrites=False):
        """
        Create a new `Engine` instance.  Arguments are as follows:

        :param controller:
          A `gc3libs.Core` instance, that will be used to operate on
          tasks.  This is the only required argument.

        :param list apps:
          Initial list of tasks to be managed by this Engine.  Tasks can
          be later added and removed with the `add` and `remove`
          methods (which see).  Defaults to the empty list.

        :param store:
          An instance of `gc3libs.persistence.Store`, or `None`.  If
          not `None`, it will be used to persist tasks after each
          iteration; by default no store is used so no task state is
          persisted.

        :param can_submit:
        :param can_retrieve:
        :param max_in_flight:
        :param max_submitted:
          Optional keyword arguments; see `Engine` for a description.
        """
        # internal-use attributes
        self._new = []
        self._in_flight = []
        self._stopped = []
        self._terminating = []
        self._terminated = []
        self._to_kill = []
        self._core = controller
        self._store = store
        for task in tasks:
            self.add(task)
        # public attributes
        self.can_submit = can_submit
        self.can_retrieve = can_retrieve
        self.max_in_flight = max_in_flight
        self.max_submitted = max_submitted
        self.output_dir = output_dir
        self.fetch_output_overwrites = fetch_output_overwrites


    def add(self, task):
        """
        Add `task` to the list of tasks managed by this Engine.
        Adding a task that has already been added to this `Engine`
        instance results in a no-op.
        """
        state = task.execution.state
        if Run.State.NEW == state:
            queue = self._new
        elif state in [Run.State.SUBMITTED, Run.State.RUNNING, Run.State.UNKNOWN]:
            queue = self._in_flight
        elif Run.State.STOPPED == state:
            queue = self._stopped
        elif Run.State.TERMINATING == state:
            queue = self._terminating
        elif Run.State.TERMINATED == state:
            queue = self._terminated
        else:
            raise AssertionError("Unhandled state '%s' in gc3libs.core.Engine." % state)
        if not _contained(task, queue):
            queue.append(task)
            task.attach(self)

    def remove(self, task):
        """Remove a `task` from the list of tasks managed by this Engine."""
        state = task.execution.state
        if Run.State.NEW == state:
            self._new.remove(task)
        elif Run.State.SUBMITTED == state or Run.State.RUNNING == state or Run.State.UNKNOWN == state:
            self._in_flight.remove(task)
        elif Run.State.STOPPED == state:
            self._stopped.remove(task)
        elif Run.State.TERMINATING == state:
            self._terminating.remove(task)
        elif Run.State.TERMINATED == state:
            self._terminated.remove(task)
        else:
            raise AssertionError("Unhandled state '%s' in gc3libs.core.Engine." % state)
        task.detach()


    def progress(self):
        """
        Update state of all registered tasks and take appropriate action.
        Specifically:

          * tasks in `NEW` state are submitted;

          * the state of tasks in `SUBMITTED`, `RUNNING`, `STOPPED` or `UNKNOWN` state is updated;

          * when a task reaches `TERMINATING` state, its output is downloaded.

          * tasks in `TERMINATED` status are simply ignored.

        The `max_in_flight` and `max_submitted` limits (if >0) are
        taken into account when attempting submission of tasks.
        """
        # prepare
        currently_submitted = 0
        currently_in_flight = 0
        if self.max_in_flight > 0:
            limit_in_flight = self.max_in_flight
        else:
            limit_in_flight = utils.PlusInfinity()
        if self.max_submitted > 0:
            limit_submitted = self.max_submitted
        else:
            limit_submitted = utils.PlusInfinity()

        # update status of SUBMITTED/RUNNING tasks before launching
        # new ones, otherwise we would be checking the status of
        # some tasks twice...
        #gc3libs.log.debug("Engine.progress: updating status of tasks [%s]"
        #                  % str.join(', ', [str(task) for task in self._in_flight]))
        transitioned = []
        for index, task in enumerate(self._in_flight):
            try:
                self._core.update_job_state(task)
                if self._store and task.changed:
                    self._store.save(task)
                state = task.execution.state
                if state == Run.State.SUBMITTED:
                    # only real applications need to be counted
                    # against the limit; policy tasks are exempt
                    # (this applies to all similar clause below)
                    if isinstance(task, Application):
                        currently_submitted += 1
                        currently_in_flight += 1
                # elif state == Run.State.RUNNING or state == Run.State.UNKNOWN:
                elif state == Run.State.RUNNING:
                    if isinstance(task, Application):
                        currently_in_flight += 1
                elif state == Run.State.STOPPED:
                    transitioned.append(index) # task changed state, mark as to remove
                    self._stopped.append(task)
                elif state == Run.State.TERMINATING:
                    transitioned.append(index) # task changed state, mark as to remove
                    self._terminating.append(task)
                elif state == Run.State.TERMINATED:
                    transitioned.append(index) # task changed state, mark as to remove
                    self._terminated.append(task)
            except gc3libs.exceptions.ConfigurationError:
                # Unrecoverable; no sense in continuing -- pass
                # immediately on to client code and let it handle
                # this...
                raise
            except Exception, x:
                gc3libs.log.error("Ignoring error in updating state of task '%s': %s: %s"
                                  % (task, x.__class__.__name__, str(x)),
                                  exc_info=True)
        # remove tasks that transitioned to other states
        for index in reversed(transitioned):
            del self._in_flight[index]

        # execute kills and update count of submitted/in-flight tasks
        #gc3libs.log.debug("Engine.progress: killing tasks [%s]"
        #                  % str.join(', ', [str(task) for task in self._to_kill]))
        transitioned = []
        for index, task in enumerate(self._to_kill):
            try:
                old_state = task.execution.state
                self._core.kill(task)
                if self._store:
                    self._store.save(task)
                if old_state == Run.State.SUBMITTED:
                    if isinstance(task, Application):
                        currently_submitted -= 1
                        currently_in_flight -= 1
                elif old_state == Run.State.RUNNING:
                    if isinstance(task, Application):
                        currently_in_flight -= 1
                self._terminated.append(task)
                transitioned.append(index)
            except Exception, x:
                if 'GC3PIE_NO_CATCH_ERRORS' in os.environ:
                    # propagate generic exceptions for debugging purposes
                    raise
                else:
                    gc3libs.log.error("Ignored error in killing task '%s': %s: %s",
                                      task, x.__class__.__name__, str(x))
                    # print again with traceback info at a higher log level
                    gc3libs.log.debug("Ignored error in killing task '%s': %s: %s",
                                      task, x.__class__.__name__, str(x), exc_info=True)
        # remove tasks that transitioned to other states
        for index in reversed(transitioned):
            del self._to_kill[index]

        # update state of STOPPED tasks; again need to make before new
        # submissions, because it can alter the count of in-flight
        # tasks.
        #gc3libs.log.debug("Engine.progress: updating status of stopped tasks [%s]"
        #                  % str.join(', ', [str(task) for task in self._stopped]))
        transitioned = []
        for index, task in enumerate(self._stopped):
            try:
                self._core.update_job_state(task)
                if self._store and task.changed:
                    self._store.save(task)
                state = task.execution.state
                if state in [Run.State.SUBMITTED, Run.State.RUNNING]:
                    if isinstance(task, Application):
                        currently_in_flight += 1
                        if task.execution.state == Run.State.SUBMITTED:
                            currently_submitted += 1
                    self._in_flight.append(task)
                    transitioned.append(index) # task changed state, mark as to remove
                elif state == Run.State.TERMINATING:
                    self._terminating.append(task)
                    transitioned.append(index) # task changed state, mark as to remove
                elif state == Run.State.TERMINATED:
                    self._terminated.append(task)
                    transitioned.append(index) # task changed state, mark as to remove
            except Exception, x:
                gc3libs.log.error("Ignoring error in updating state of STOPPED task '%s': %s: %s"
                                  % (task, x.__class__.__name__, str(x)),
                                  exc_info=True)
        # remove tasks that transitioned to other states
        for index in reversed(transitioned):
            del self._stopped[index]

        # now try to submit NEW tasks
        #gc3libs.log.debug("Engine.progress: submitting new tasks [%s]"
        #                  % str.join(', ', [str(task) for task in self._new]))
        transitioned = []
        if self.can_submit:
            index = 0
            while (currently_submitted < limit_submitted
                   and currently_in_flight < limit_in_flight
                   and index < len(self._new)):
                task = self._new[index]
                # try to submit; go to SUBMITTED if successful, FAILED if not
                if currently_submitted < limit_submitted and currently_in_flight < limit_in_flight:
                    try:
                        self._core.submit(task)
                        if self._store:
                            self._store.save(task)
                        self._in_flight.append(task)
                        transitioned.append(index)
                        if isinstance(task, Application):
                            currently_submitted += 1
                            currently_in_flight += 1
                    except Exception, x:
                        if 'GC3PIE_NO_CATCH_ERRORS' in os.environ:
                            # propagate generic exceptions for debugging purposes
                            raise
                        else:
                            gc3libs.log.error(
                                "Ignored error in submitting task '%s': %s: %s",
                                task, x.__class__.__name__, str(x))
                            # print again with traceback at a higher log level
                            gc3libs.log.debug(
                                "Ignored error in submitting task '%s': %s: %s",
                                task, x.__class__.__name__, str(x), exc_info=True)
                            # record the fact in the task's history
                            task.execution.history(
                                "Submission failed: %s: %s"
                                % (x.__class__.__name__, str(x)))
                index += 1
        # remove tasks that transitioned to SUBMITTED state
        for index in reversed(transitioned):
            del self._new[index]

        # finally, retrieve output of finished tasks
        #gc3libs.log.debug("Engine.progress: fetching output of tasks [%s]"
        #                  % str.join(', ', [str(task) for task in self._terminating]))
        if self.can_retrieve:
            transitioned = []
            for index, task in enumerate(self._terminating):
                # try to get output
                try:
                    self._core.fetch_output(task)
                except gc3libs.exceptions.UnrecoverableDataStagingError, ex:
                    gc3libs.log.error("Error in fetching output of task '%s',"
                                      " will mark it as TERMINATED"
                                      " (with error exit code %d): %s: %s",
                                      task, posix.EX_IOERR,
                                      ex.__class__.__name__, str(ex), exc_info=True)
                    task.execution.returncode = (Run.Signals.DataStagingFailure,
                                                 posix.EX_IOERR)
                    task.execution.state = Run.State.TERMINATED
                    task.changed = True
                except Exception, x:
                    if 'GC3PIE_NO_CATCH_ERRORS' in os.environ:
                        # propagate generic exceptions for debugging purposes
                        raise
                    else:
                        gc3libs.log.error(
                            "Ignored error in fetching output of task '%s': %s: %s",
                            task, x.__class__.__name__, str(x))
                        gc3libs.log.debug(
                            "Ignored error in fetching output of task '%s': %s: %s",
                            task, x.__class__.__name__, str(x), exc_info=True)
                if task.execution.state == Run.State.TERMINATED:
                    self._terminated.append(task)
                    self._core.free(task)
                    transitioned.append(index)
                if self._store and task.changed:
                    self._store.save(task)
            # remove tasks for which final output has been retrieved
            for index in reversed(transitioned):
                del self._terminating[index]


    def stats(self, only=None):
        """

        Return a dictionary mapping each state name into the count of
        tasks in that state. In addition, the following keys are defined:

        * `ok`:  count of TERMINATED tasks with return code 0

        * `failed`: count of TERMINATED tasks with nonzero return code

        * `total`: total count of managed tasks, whatever their state

        If the optional argument `only` is not None, tasks whose
        whose class is not contained in `only` are ignored.
        : param tuple only: Restrict counting to tasks of these classes.

        """
        if only:
            gc3libs.log.debug(
                "Engine.stats: Restricting to object of class '%s'", only.__name__)
        result = defaultdict(lambda: 0)
        if only:
            result[Run.State.NEW] = len([task for task in self._new
                                                       if isinstance(task, only)])
        else:
            result[Run.State.NEW] = len(self._new)
        for task in self._in_flight:
            if only and not isinstance(task, only):
                continue
            state = task.execution.state
            result[state] += 1
        for task in self._stopped:
            if only and not isinstance(task, only):
                continue
            state = task.execution.state
            result[state] += 1
        for task in self._to_kill:
            if only and not isinstance(task, only):
                continue
            # XXX: presumes no task in the `_to_kill` list is TERMINATED
            state = task.execution.state
            result[state] += 1
        if only:
            result[Run.State.TERMINATING] += len([task for task in self._terminating
                                                               if isinstance(task, only)])
        else:
            result[Run.State.TERMINATING] += len(self._terminating)
        if only:
            result[Run.State.TERMINATED] += len([task for task in self._terminated
                                                               if isinstance(task, only)])
        else:
            result[Run.State.TERMINATED] += len(self._terminated)

        # for TERMINATED tasks, compute the number of successes/failures
        for task in self._terminated:
            if only and not isinstance(task, only):
                continue
            if task.execution.returncode == 0:
                result['ok'] += 1
            else:
                # gc3libs.log.debug(
                #     "Task '%s' failed: return code %s (signal %s, exitcode %s)"
                #     % (task, task.execution.returncode,
                #        task.execution.signal, task.execution.exitcode))
                result['failed'] += 1
        result['total'] = (result[Run.State.NEW]
                           + result[Run.State.SUBMITTED]
                           + result[Run.State.RUNNING]
                           + result[Run.State.STOPPED]
                           + result[Run.State.TERMINATING]
                           + result[Run.State.TERMINATED]
                           + result[Run.State.UNKNOWN])
        return result


    # implement a Core-like interface, so `Engine` objects can be used
    # as substitutes for `Core`.

    def free(self, task, **extra_args):
        """
        Proxy for `Core.free`, which see.
        """
        self._core.free(task)


    def submit(self, task, resubmit=False, **extra_args):
        """
        Submit `task` at the next invocation of `perform`.

        The `task` state is reset to ``NEW`` and then added to the
        collection of managed tasks.
        """
        if resubmit:
            task.execution.state = Run.State.NEW
        return self.add(task)


    def update_job_state(self, *tasks, **extra_args):
        """
        Return list of *current* states of the given tasks.  States
        will only be updated at the next invocation of `progress`; in
        particular, no state-change handlers are called as a result of
        calling this method.
        """
        pass


    def fetch_output(self, task, output_dir=None, overwrite=False, **extra_args):
        """
        Enqueue task for later output retrieval.

        .. warning:: FIXME

          The `output_dir` and `overwrite` parameters are currently ignored.

        """
        self.add(task)


    def kill(self, task, **extra_args):
        """
        Schedule a task for killing on the next `progress` run.
        """
        self._to_kill.append(task)


    def peek(self, task, what='stdout', offset=0, size=None, **extra_args):
        """
        Proxy for `Core.peek` (which see).
        """
        self._core.peek(task, what, offset, size, **extra_args)


    def close(self):
        """
        Call explicilty finalize methods on relevant objects
        e.g. LRMS
        """
        self._core.close()

    # Wrapper methods around `Core` to access the backends directly
    # from the `Engine`.

    @utils.same_docstring_as(Core.select_resource)
    def select_resource(self, match):
        return self._core.select_resource(match)

    @utils.same_docstring_as(Core.get_resources)
    def get_resources(self):
        return self._core.get_resources()

    @utils.same_docstring_as(Core.get_backend)
    def get_backend(self, name):
        return self._core.get_backend(name)
