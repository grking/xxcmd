# mock_curses.py
# Mock basic curses functions for unit testing


class stdscr:

    @classmethod
    def keypad(cls, enable):
        pass

    @classmethod
    def getmaxyx(cls):
        return (80, 20)

    @classmethod
    def addstr(cls, y, x, text, attrib):
        pass

    @classmethod
    def clrtoeol(cls):
        pass

    @classmethod
    def move(cls, y, x):
        pass

    @classmethod
    def refresh(cls):
        pass

    @classmethod
    def box(cls):
        pass

    @classmethod
    def hline(cls, y, x, ch, w):
        pass

    @classmethod
    def addch(cls, y, x, ch):
        pass


class curses:

    A_NORMAL = 0
    A_REVERSE = 1
    A_BOLD = 2
    ACS_HLINE = 3
    ACS_LTEE = 4
    ACS_RTEE = 5

    @classmethod
    def initscr(cls):
        return stdscr

    @classmethod
    def noecho(cls):
        pass

    @classmethod
    def cbreak(cls):
        pass

    @classmethod
    def nocbreak(cls):
        pass

    @classmethod
    def echo(cls):
        pass

    @classmethod
    def endwin(cls):
        pass

    @classmethod
    def curs_set(cls, value):
        pass
