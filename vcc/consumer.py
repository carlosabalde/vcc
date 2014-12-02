# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import time
import os
import json
import multiprocessing
import signal
import threading
from vcc.helpers import varnish
from vcc import counters


class Worker(multiprocessing.Process):
    def __init__(self, ppid, shutdown_event, options, ipc_queue):
        super(Worker, self).__init__(name='consumer')
        self.__ppid = ppid
        self.__shutdown_event = shutdown_event
        self.__stopping = False
        self._ipc_queue = ipc_queue
        self._options = options

    def run(self):
        try:
            # Adjust inherited signal handlers.
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            signal.signal(signal.SIGCHLD, signal.SIG_DFL)

            # Specific worker initialization.
            self._init()

            # Periodically check for termination.
            while not self.__stopping:
                # Check if the parent process is still alive.
                if self.__ppid is not None and os.getppid() != self.__ppid:
                    self.__stopping = True
                # Check if the parent process has requested shutdown.
                elif self.__shutdown_event and self.__shutdown_event.is_set():
                    self.__stopping = True
                # Poll worker & wait for the next check.
                else:
                    self._poll()
                    time.sleep(1.0)
        except Exception as e:
            raise e
        finally:
            self._shutdown()

    def _init(self):
        raise NotImplementedError('Please implement this method.')

    def _poll(self):
        raise NotImplementedError('Please implement this method.')

    def _shutdown(self):
        raise NotImplementedError('Please implement this method.')


class Consumer(Worker):
    def _init(self):
        # Base initializations.
        self.__thread = None
        self.__last_event = 0
        self.__last_submission = 0
        self.__data = {}
        self.__mutex = threading.Lock()

        # Create VSL wrapper.
        if self._options.version == 3:
            self.__vsl = varnish.VSL3(self._options.lib)
        else:
            raise RuntimeError('Varnish version %d is not supported.' % self._options.version)
        if self._options.name is not None:
            self.__vsl.arg('n', self._options.name)
        self.__vsl.arg('i', 'VCL_Log')
        self.__vsl.open(nb=0)

        # Launch main thread.
        self.__thread = threading.Thread(target=self._thread_loop)
        self.__thread.daemon = True
        self.__thread.start()

    def _poll(self):
        # Initializations.
        now = time.time()

        # Is the main thread still alive?
        if not self.__thread.is_alive():
            raise Exception('Consumer thread has been unexpectedly stopped.')

        # Submit counters to the parent process?
        if now - self.__last_submission > 1.0:
            window = int(now) - int(now) % self._options.wsize
            with self.__mutex:
                # Drop outdated windows.
                self._drop(window)

                # Submit.
                self._submit(window)
                self.__last_submission = now

        # Reopen VSL is it went silent during 5 or more seconds.
        if now - self.__last_event > 5.0:
            self.__vsl.reopen()
            self.__last_event = now

    def _shutdown(self):
        pass

    def _thread_loop(self):
        self.__vsl.dispatch(self._callBack)

    def _callBack(self, priv, tag, fd, length, spec, ptr, bm):
        # General initializations.
        now = time.time()
        self.__last_event = now

        # Is this a relevant event?
        if ptr.startswith(self._options.prefix):
            items = ptr[len(self._options.prefix):int(length)].split(':', 3)
            if len(items) == 3:
                with self.__mutex:
                    # Initializations.
                    counter = None
                    name, op, value = items

                    # Create / fetch counter instance.
                    window = int(now) - int(now) % self._options.wsize
                    if name not in self.__data:
                        self.__data[name] = {}
                    if window not in self.__data[name] or \
                       self.__data[name][window].op != op:
                        counter = counters.instance(op)
                        if counter is not None:
                            self.__data[name][window] = counter
                    else:
                        counter = self.__data[name][window]

                    # Append new value.
                    if counter is not None:
                        counter.append(value)

    def _drop(self, current_window):
        min_window = current_window - self._options.nwindows * self._options.wsize
        for name, windows in self.__data.iteritems():
            new_windows = {}
            for tst, counter in windows.iteritems():
                if tst >= min_window:
                    new_windows[tst] = counter
            self.__data[name] = new_windows

    def _submit(self, current_window):
        counters = []
        for name, windows in self.__data.iteritems():
            values = []
            for offset in range(self._options.nwindows):
                tst = current_window - offset * self._options.wsize
                if tst in windows:
                    values.append(windows[tst].value)
                else:
                    values.append(None)
            counters.append((name, values))

        self._ipc_queue.put_nowait(json.dumps(counters))
