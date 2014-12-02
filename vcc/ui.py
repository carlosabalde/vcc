# -*- coding: utf-8 -*-

'''
:copyright: (c) 2014 by Carlos Abalde, see AUTHORS.txt for more details.
'''

from __future__ import absolute_import
import datetime
import curses
import threading


class UI(threading.Thread):
    KEY_ESC = 27

    MIN_WIDTH = 12
    INTEGER_FORMAT = '%d'
    DECIMAL_FORMAT = '%.5f'

    def __init__(self, options):
        super(UI, self).__init__()
        self.daemon = True
        self.__options = options
        self.__mutex = threading.Lock()
        self.__stopping = threading.Event()
        self.__pad = None

    def run(self):
        # General initializations.
        pminrow = 0
        pmincolumn = 0
        wmessage = '      Waiting for data      '
        lheader = ' Varnish Custom Counters (name=%s, wsize=%d, nwindows=%d)' % (
            self.__options.name if self.__options.name is not None else '-',
            self.__options.wsize,
            self.__options.nwindows,
        )

        # Screen initializations.
        screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        screen.keypad(1)
        screen.timeout(250)

        # Event loop.
        while not self.stopping:
            # Wait (up to 250 ms) for some user input.
            ch = screen.getch()

            # Extract current screen dimensions (excluding top bar).
            srows, scolumns = screen.getmaxyx()
            srows -= 1

            # Safely render pad contents.
            with self.__mutex:
                # Select pad to be rendered.
                if self.__pad is None:
                    wmessage = wmessage[1:] + wmessage[0]
                    pad = curses.newpad(srows, scolumns)
                    pad.addstr(
                        int(srows / 2),
                        max(int(scolumns / 2 - len(wmessage) / 2), 0),
                        wmessage, curses.A_REVERSE | curses.A_BOLD)
                else:
                    pad = self.__pad

                # Extract pad dimensions, expand & update dimensions.
                prows, pcolumns = pad.getmaxyx()
                pad.resize(max(srows, prows), max(scolumns, pcolumns))
                prows, pcolumns = pad.getmaxyx()

                # Check requested action, if any.
                if ch == ord('q') or ch == ord('Q') or ch == self.KEY_ESC:
                    self.stop()
                elif ch == curses.KEY_RESIZE:
                    pminrow = 0
                    pmincolumn = 0
                elif ch == curses.KEY_UP or ch == curses.KEY_PPAGE:
                    pminrow = max(pminrow - srows, 0)
                elif ch == curses.KEY_DOWN or ch == curses.KEY_NPAGE:
                    pminrow = min(pminrow + srows, prows - srows)
                elif ch == curses.KEY_LEFT:
                    pmincolumn = max(pmincolumn - scolumns, 0)
                elif ch == curses.KEY_RIGHT:
                    pmincolumn = min(pmincolumn + scolumns, pcolumns - scolumns)
                elif ch != -1:
                    curses.beep()

                # Update top bar.
                screen.addstr(0, 0, ' ' * scolumns, curses.A_REVERSE)
                if len(lheader) < scolumns:
                    screen.addstr(0, 0, lheader, curses.A_REVERSE | curses.A_BOLD)
                rheader = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' '
                if len(lheader) + len(rheader) < scolumns:
                    screen.addstr(0, scolumns - len(rheader), rheader, curses.A_REVERSE | curses.A_BOLD)

                # Render pad.
                pad.refresh(pminrow, pmincolumn, 1, 0, srows, scolumns - 1)

        # Destroy screen.
        curses.nocbreak()
        curses.echo()
        screen.keypad(0)
        curses.endwin()

    def update(self, counters):
        pad = None
        if len(counters) > 0:
            # Sort incoming counters (incrementally by counter name).
            counters.sort(key=lambda item: item[0])

            # Create new pad.
            prows = 2 + len(counters)
            pcolumns = 1 + len(max([name for (name, values) in counters], key=len)) + 1
            pad = curses.newpad(prows, pcolumns)

            # Add first column (counter names).
            pad.addstr(1, 0, '-' * pcolumns)
            for (i, (name, values)) in enumerate(counters):
                pad.addstr(2 + i, 1, name)

            # Add rest of columns (counter values).
            for offset in range(self.__options.nwindows):
                # Render column.
                column = ['N-%d ' % offset if offset > 0 else 'N ', '']
                for (i, (name, values)) in enumerate(counters):
                    if offset < len(values) and values[offset] is not None:
                        value = values[offset]
                        if isinstance(value, (int, long)):
                            value = self.INTEGER_FORMAT % value
                        elif isinstance(value, float):
                            value = self.DECIMAL_FORMAT % value
                        column.append(value + ' ')
                    else:
                        column.append('- ')
                width = max(len(max(column, key=len)) + 1, self.MIN_WIDTH)
                column[1] = '-' * width

                # Add column.
                pcolumns += width
                pad.resize(prows, pcolumns)
                for (i, value) in enumerate(column):
                    pad.addstr(i, pcolumns - len(value) - 1, value)

        # Safely update pad.
        with self.__mutex:
            self.__pad = pad

    def stop(self):
        self.__stopping.set()

    @property
    def stopping(self):
        return self.__stopping.isSet()
