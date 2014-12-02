# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import os
import argparse
import json
import signal
import time
import multiprocessing
import Queue
import errno
from vcc.helpers import log
from vcc.consumer import Consumer
from vcc.ui import UI


class Runner(object):
    def __init__(self, options):
        # General initializations.
        self.__options = options
        self.__stopping = False

        # Set up signal handlers.
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGCHLD, self._signal_handler)

    def run(self):
        # General initializations.
        log.reset()
        pid = os.getpid()
        shutdown_event = multiprocessing.Event()
        ipc_queue = multiprocessing.Queue(-1)

        # Launch consumer process.
        consumer = Consumer(pid, shutdown_event, self.__options, ipc_queue)
        consumer.start()

        # Launch UI thread.
        ui = UI(self.__options)
        ui.start()

        # Periodically check for (1) unexpected terminations of the consumer
        # process; (2) terminations of the main process; and (3) terminations
        # of the UI thread.
        while not self.__stopping and not ui.stopping:
            try:
                data = json.loads(ipc_queue.get(True, 0.250))
                if data is not None:
                    ui.update(data)
            except Queue.Empty:
                pass
            except IOError as e:
                if e.errno != errno.EINTR:
                    raise

        # Stop UI thread.
        if not ui.stopping:
            ui.stop()

        # Set shutdown event and wait a few seconds for a graceful shutdown
        # of the consumer process.
        shutdown_event.set()
        retries = 5
        while retries > 0:
            if consumer.is_alive():
                retries = retries - 1
                time.sleep(0.1)
            else:
                break

        # After timeout, force shutdown of the consumer process.
        if consumer.is_alive():
            consumer.terminate()

        # Wait for termination of the consumer process.
        consumer.join()

    def _signal_handler(self, *args):
        self.__stopping = True


def _check_wsize(raw):
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError('a value grater than 0 is required')
    return value


def _check_nwindows(raw):
    value = int(raw)
    if value <= 0 or value >= 100:
        raise argparse.ArgumentTypeError('a value grater than 0 and less that 100 is required')
    return value


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--version', dest='version', type=int, choices=(3, 4), required=True,
        help='set version of the varnishd instance')
    parser.add_argument(
        '--name', dest='name', type=str, default=None,
        help='set the name of the varnishd instance to get logs from')
    parser.add_argument(
        '--wsize', dest='wsize', type=_check_wsize, default=60,
        help='set the window size (in seconds)')
    parser.add_argument(
        '--nwindows', dest='nwindows', type=_check_nwindows, default=10,
        help='set the number of windows in the time series')
    parser.add_argument(
        '--lib', dest='lib', type=str, default='libvarnishapi.so.1',
        help='set the varnishd API shared library')
    parser.add_argument(
        '--prefix', dest='prefix', type=str, default='vcc:',
        help='set the logging prefix')

    Runner(parser.parse_args()).run()


if __name__ == '__main__':
    main()
