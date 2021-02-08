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


class curses:

    A_NORMAL = 0
    A_REVERSE = 1

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
