# cmdmanager.py
import os
import curses
import subprocess
import urllib3
from .dbitem import DBItem


# Where do we store our database of commands?
DEFAULT_DATABASE_FILE = "~/.xxcmd"

# What shell do we use to execute commands?
DEFAULT_SHELL = '/usr/bin/bash'


class CmdManager():

    def __init__(self):
        # Our cmd database
        self.database = []
        # Our curses window
        self.win = None
        # And dimensions of it
        self.win_width = 0
        self.win_height = 0
        # Our current search string
        self.search = ''
        # Our current search results
        self.results = []
        # Our current selection row
        self.selection = 1
        # Auto run command if only one search result
        self.autorun = False
        # Display options
        self.align = True  # Align commands after labels
        self.show_labels = True  # Show labels?
        # Our default data filename
        self.filename = DEFAULT_DATABASE_FILE
        # The shell we'll use to execute commands
        self.shell = DEFAULT_SHELL

    # Get contents of file, return a list of lines
    def get_file_contents(self, filename):
        filename = os.path.expanduser(filename)
        if not os.path.isfile(filename):
            return False
        # Return file contents
        # Allow exceptions to raise here, if we can't read this
        # something is horribly wrong
        f = open(filename, "rt")
        lines = [x.strip() for x in f.readlines()]
        f.close()
        return lines

    # Get URL contents
    def get_url_contents(self, url):

        if url.startswith('file://'):
            # fake it for testing
            resp = type('', (), {})()
            resp.status = 200
            resp.data = "\n".join(
                self.get_file_contents(url[7:])).encode('utf-8')
        else:
            # Load data from an actual URL
            http = urllib3.PoolManager()
            resp = http.request('GET', url)

        if not resp.status == 200:
            print(f"Could not retrieve url ({resp.status})")
            return False

        # Get data
        lines = resp.data.decode('utf-8')
        if '\r\n' in lines:
            lines = lines.split("\r\n")
        elif '\n\r' in lines:
            lines = lines.split("\n\r")
        elif '\n' in lines:
            lines = lines.split("\n")
        elif '\r' in lines:
            lines = lines.split("\r")
        lines = [x.strip() for x in lines]
        return lines

    def import_database(self, url):
        data = self.get_url_contents(url)
        if not data:
            return False
        self.load_database(True, data)
        self.save_database()
        return True

    # Load (optionally merge) some data into our database
    # data should be an iterable of lines
    def load_database(self, merge=False, data=None):

        # Start from scratch
        if not merge:
            self.database.clear()

        # If we aren't passed any data, load our default file
        if not data:
            data = self.get_file_contents(self.filename)
            if not data:
                return False

        # Load each line
        for line in data:
            # Skip empty
            if not line.strip():
                continue
            self.add_database_entry(line, True)
        return True

    # Save our DB
    def save_database(self):
        dbname = os.path.expanduser(self.filename)
        f = open(dbname, "wt")
        for item in self.database:
            f.write(f"{item.cmd} [{item.label}]\n")
        f.close()

    # Print all commands
    def print_commands(self):
        for item in self.database:
            print(item.pretty(0, self.show_labels))

    # Add an item to our DB
    def add_database_entry(self, entry, disable_save=False):

        if type(entry) is DBItem:
            newitem = entry
        else:
            newitem = DBItem(entry)

        for item in self.database:
            if item.cmd == newitem.cmd and item.label == newitem.label:
                return False

        self.database.append(newitem)
        if not disable_save:
            self.save_database()
        return True

    # Delete a database entry
    def delete_database_entry(self, dbitem, disable_save=False):
        for item in self.database:
            if item.cmd == dbitem.cmd and item.label == dbitem.label:
                self.database.remove(item)
                break
        if not disable_save:
            self.save_database()

    # Initialise our display
    def initialise_display(self):
        curses.set_escdelay(1)
        self.win = curses.initscr()
        curses.noecho()
        self.win.keypad(True)
        curses.cbreak()
        self.win_height, self.win_width = self.win.getmaxyx()

    # Finalise our display
    def finalise_display(self):
        curses.nocbreak()
        curses.echo()
        self.win.keypad(False)
        curses.endwin()
        self.win = None

    # Calculate search results
    def update_search(self):
        self.results.clear()
        for item in self.database:
            if self.search.lower() in item.search_key():
                self.results.append(item)
        self.constrain_selection()

    # Update our window output
    def redraw(self):
        # Top search line
        self.win.addstr(0, 0, f"{self.search}")
        self.win.clrtoeol()

        # Determine max label length for indenting
        indent = 0
        if self.align:
            for item in self.results:
                if len(item.label) > indent:
                    indent = len(item.label)
            indent += 2

        # Search results
        for i in range(1, self.win_height):
            attrib = curses.A_NORMAL
            if i == self.selection:
                attrib = curses.A_REVERSE
            if i > len(self.results):
                self.win.addstr(i, 0, "", attrib)
                self.win.clrtoeol()
            else:
                item = self.results[i-1]
                item = item.pretty(indent, self.show_labels)
                self.win.addstr(i, 0, f"{item}", attrib)
                self.win.clrtoeol()

        self.win.move(0, len(self.search))
        self.win.refresh()

    # Get the selected line
    def get_selection(self):
        idx = self.selection - 1
        if self.results and idx >= 0 and idx < len(self.results):
            return self.results[idx]

    # Ensure the selection is in bounds
    def constrain_selection(self):
        if self.selection < 1:
            self.selection = 1
        if self.selection > len(self.results):
            self.selection = len(self.results)

    # Get input
    def get_input(self):

        try:
            key = self.win.getkey()
        except KeyboardInterrupt:
            exit(0)

        if key == 'KEY_BACKSPACE':
            self.search = self.search[:-1]
        elif key == 'KEY_DOWN':
            self.selection += 1
            self.constrain_selection()
        elif key == 'KEY_UP':
            self.selection -= 1
            self.constrain_selection()
        elif key == '\x1b':
            exit(0)
        elif key == 'KEY_DC':
            self.delete_database_entry(self.get_selection())
        elif key == "\n":
            self.execute_command(self.get_selection())
        elif len(key) > 1:
            pass
        else:
            self.search += key

    # Shell execute a command
    def execute_command(self, dbitem, replace_process=True):
        if not dbitem or not dbitem.cmd:
            return

        self.finalise_display()

        # We support not replacing the current process just for testing
        params = [os.path.basename(self.shell), '-c'] + [dbitem.cmd]
        if replace_process:
            print(dbitem.cmd)
            os.execv(self.shell, params)
        else:
            result = subprocess.run(params, capture_output=True)
            return result.stdout.decode('utf-8').strip()

    # Check and execute auto run
    def do_autorun(self):
        # Auto run?
        if self.autorun and len(self.results) == 1:
            self.execute_command(self.get_selection())
        # Only one try at this
        self.autorun = False

    # Run
    def run(self, cmd=''):

        if cmd:
            self.search = cmd
            self.autorun = True

        if not self.database:
            print("No database. Add commands with: xx -a [label] <command>")
            exit(1)

        self.initialise_display()

        try:
            while True:
                self.update_search()
                self.do_autorun()
                self.redraw()
                self.get_input()
        finally:
            self.finalise_display()
