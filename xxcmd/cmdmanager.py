# cmdmanager.py
import os
import subprocess
import urllib.request
from .dbitem import DBItem
from .consoleui import ConsoleUI
from .config import Config


# Where is the system-wide database of commands?
DEFAULT_SYSTEM_DATABASE_FILE = '/etc/xxcmd'

# Where do we store our database of commands?
DEFAULT_DATABASE_FILE = "~/.xxcmd"

# What shell do we use to execute commands?
if 'SHELL' in os.environ:
    DEFAULT_SHELL = os.environ['SHELL']
else:
    DEFAULT_SHELL = '/bin/sh'

# A few default database commands if there is no database after
# first install
DEFAULT_COMMANDS = [
    '[File Sizes] du --max-depth=1 -h .',
    '''[Show CPUs] cat /proc/cpuinfo | grep "model name" | awk -F: '{print $2}' | uniq -c'''
]


class UnitTestException(Exception):
    pass


class CmdManager():

    # selected_row - row index of highlight item
    @property
    def selected_row(self):
        return self._selected_row

    @selected_row.setter
    def selected_row(self, value):
        self._selected_row = value
        if self._selected_row < 0:
            self._selected_row = 0
        if self._selected_row >= len(self.results):
            self._selected_row = len(self.results)-1

    # selected_item - dbitem instance at selected row
    @property
    def selected_item(self):
        idx = self.selected_row
        if self.results and idx >= 0 and idx < len(self.results):
            return self.results[idx]

    # Mode
    @property
    def mode(self):
        return self._mode

    def __init__(self):
        # Default config
        self.config = Config()
        # Our cmd database
        self.database = []
        # Flag for if the file even exists
        self.database_exists = True
        # Our UI
        self.ui = ConsoleUI(self)
        # Our current search results
        self.results = []
        # Our current selection row
        self._selected_row = 0
        # Our default data filename
        self.filename = DEFAULT_DATABASE_FILE
        # Our default system data filename
        self.sysfilename = DEFAULT_SYSTEM_DATABASE_FILE
        # The shell we'll use to execute commands
        self.shell = DEFAULT_SHELL
        if self.config.shell.lower() != 'default':
            self.shell = self.config.shell
        # Default mode
        self._mode = ''
        self.search_mode()
        # Saving disabled?
        self.save_disabled = False

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
            resp = "\n".join(
                self.get_file_contents(url[7:])).encode('utf-8')
        else:
            # Load data from an actual URL
            try:
                resp = urllib.request.urlopen(url).read()
            except Exception as ex:
                print("Could not retrieve url: {0}".format(ex))
                return False

        # Get data
        lines = resp.decode('utf-8')
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

    def import_database_url(self, url):
        data = self.get_url_contents(url)
        if not data:
            return False
        self.load_data(data, True)
        self.save_database()
        return True

    # Load (optionally merge) some data into our database
    # data should be an iterable of lines
    def load_data(self, data, merge=False, tags=None):

        # Start from scratch
        if not merge:
            self.database.clear()

        # If we aren't passed any data, bail out
        if not data:
            return

        # Load each line
        for line in data:
            # Skip empty
            if not line.strip():
                continue
            self.save_disabled = True
            try:
                self.add_database_entry(line, tags)
            except Exception as ex:
                raise ex
            finally:
                self.save_disabled = False

        return True

    # Load a command database from a file
    def load_file(self, filename, merge=False, tags=None):

        data = self.get_file_contents(filename)
        if not data:
            return False

        return self.load_data(data, merge, tags)

    # Load default databases
    def load_databases(self):
        merge = False
        globalfile = False
        # Try the system global database
        if self.config.load_global_database:
            globalfile = self.load_file(self.sysfilename, merge, ['global'])
            merge = True

        # Try the local user database
        localfile = self.load_file(self.filename, merge)
        if localfile is False:
            self.database_exists = False
        # Return if we loaded anything at all
        return globalfile or localfile

    # Resort, if required
    def sort(self):
        if self.config.sort_by_label:
            if self.config.sort_case_sensitive:
                self.results.sort(key=lambda x: x.label, reverse=False)
            else:
                self.results.sort(key=lambda x: x.label.lower(), reverse=False)
        elif self.config.sort_by_command:
            if self.config.sort_case_sensitive:
                self.results.sort(key=lambda x: x.cmd, reverse=False)
            else:
                self.results.sort(key=lambda x: x.cmd.lower(), reverse=False)

    # Save our DB
    def save_database(self):
        # Don't bother if disabled
        if self.save_disabled:
            return
        # Save to our user dir
        dbname = os.path.expanduser(self.filename)
        f = open(dbname, "wt")
        for item in self.database:
            # Don't save items from the system global database
            if not self.is_global(item):
                f.write("{0} [{1}]\n".format(item.cmd, item.label))
        f.close()

    # Print all commands
    def print_commands(self):
        for item in self.database:
            if self.config.show_labels:
                print("[{0}] {1}".format(item.label, item.cmd))
            else:
                print("{0}".format(item.cmd))

    # Add an item to our DB
    def add_database_entry(self, entry, tags=None):

        if type(entry) is DBItem:
            newitem = entry
        else:
            newitem = DBItem(entry)

        # Add item tags
        if tags:
            for tag in tags:
                if tag not in newitem.tags:
                    newitem.tags.append(tag)

        for item in self.database:
            if item.cmd == newitem.cmd and item.label == newitem.label:
                return False

        self.database.append(newitem)
        # We can't be editing stuff now, default to search mode
        self.search_mode()

        self.save_database()

        return True

    # Delete a database entry
    def delete_database_entry(self, dbitem):
        # Sanity check
        if not dbitem:
            return

        for item in self.database:
            if item.cmd == dbitem.cmd and item.label == dbitem.label:
                self.database.remove(item)
                break
        self.save_database()

    # Add a new command from the edit line
    def add_new_command(self):
        self.add_database_entry(self.ui.input.value)

    # Delete the selected database entry
    def delete_selected_database_entry(self):
        if self.is_global(self.selected_item):
            self.ui.flash(
                "Can't edit items from the system-wide database ({0})".format(
                    self.sysfilename))
            return
        self.delete_database_entry(self.selected_item)

    # Search for something
    def _search(self, searchterm, labels=False, commands=False):
        for item in self.database:
            matched = False
            if labels and item.label:
                matched = searchterm in item.label.lower()
            if commands and not matched:
                matched = searchterm in item.cmd.lower()
            if matched:
                self.results.append(item)

    # Calculate search results
    def update_search(self):
        self.results.clear()

        # Special case of no search term
        if not self.ui.input.value:
            self.results = self.database[:]
        # Search labels, then commands if no labels found
        elif self.config.search_labels_first:
            self._search(self.ui.input.value.lower(), True, False)
            if not len(self.results):
                self._search(self.ui.input.value.lower(), False, True)
        # Search labels only
        elif self.config.search_labels_only:
            self._search(self.ui.input.value.lower(), True, False)
        # Search both labels and command
        else:
            self._search(self.ui.input.value.lower(), True, True)

        # Refresh selection
        self.selected_row = self.selected_row

        # Sort the results
        self.sort()

    # Move the selected row down
    def selection_down(self):
        self.selected_row += 1

    # Move the selected row up
    def selection_up(self):
        self.selected_row -= 1

    # Enter edit new command
    def edit_newcmd_mode(self):
        if not self.selected_item:
            return
        self.ui.input_prefix = 'New Cmd: '
        self.ui.input.set_value('')
        self.ui.key_events = {
            '\x1b': self.search_mode,  # escape - exit mode
            "\n": self.add_new_command  # Return
        }
        self._mode = 'edit'

    # Enter edit label mode
    def edit_label_mode(self):
        if not self.selected_item:
            return
        self.ui.input_prefix = 'Edit Label: '
        self.ui.input.set_value(self.selected_item.label)
        self.ui.key_events = {
            '\x1b': self.search_mode,  # escape - exit mode
            "\n": self.update_selected_label  # Return
        }
        self._mode = 'edit'

    # Enter edit command mode
    def edit_command_mode(self):
        if not self.selected_item:
            return
        self.ui.input_prefix = 'Edit Cmd: '
        self.ui.input.set_value(self.selected_item.cmd)
        self.ui.key_events = {
            '\x1b': self.search_mode,  # escape - exit mode
            "\n": self.update_selected_command  # Return
        }
        self._mode = 'edit'

    # Enter search mode
    def search_mode(self):
        self.ui.input_prefix = 'Search: '
        self.ui.input.pop_value()
        self.ui.key_events = {
            'KEY_DOWN': self.selection_down,  # Down arrow
            'KEY_UP': self.selection_up,  # Up arrow
            '\x1b': exit,  # escape
            'KEY_F(1)': self.edit_label_mode,  # F1
            'KEY_F(2)': self.edit_command_mode,  # F2
            'KEY_F(3)': self.edit_newcmd_mode,  # F3
            '\x09': self.edit_command_mode,  # Ctrl+I
            '\x05': self.edit_label_mode,  # Ctrl+E
            '\x07': self.edit_newcmd_mode,  # Ctrl+G
            'KEY_DC': self.delete_selected_database_entry,  # Delete
            "\n": self.execute_selected_command,  # Return
            'ALWAYS': self.update_search
        }
        self._mode = 'search'
        self.update_search()

    # Check if an item is a global config item
    def is_global(self, item):
        return item and 'global' in item.tags

    # Update the selected items label
    def update_selected_label(self):
        if self.is_global(self.selected_item):
            self.ui.flash(
                "Can't edit items from the system-wide database ({0})".format(
                    self.sysfilename))
            self.search_mode()
            return
        self.selected_item.label = self.ui.input.value
        self.save_database()
        self.search_mode()

    # Update the selected items command
    def update_selected_command(self):
        if self.is_global(self.selected_item):
            self.ui.flash(
                "Can't edit items from the system-wide database ({0})".format(
                    self.sysfilename))
            self.search_mode()
            return
        self.selected_item.cmd = self.ui.input.value
        self.save_database()
        self.search_mode()

    # Execute the selected command
    def execute_selected_command(self):
        self.execute_command(self.selected_item)

    # Shell execute a command
    def execute_command(self, dbitem, replace_process=True):
        if not dbitem or not dbitem.cmd:
            return

        # Our process is about to be replaced, normal orderly
        # shutdown won't happen
        self.ui.finalise_display()

        # We support not replacing the current process just for testing
        params = [os.path.basename(self.shell), '-c'] + [dbitem.cmd]
        if replace_process:
            if self.config.echo_commands:
                print(dbitem.cmd)
            os.execv(self.shell, params)
        else:
            result = subprocess.check_output(dbitem.cmd.split())
            return result.decode('utf-8').strip()

    # Check and execute auto run
    def do_autorun(self):
        # Auto run?
        self.update_search()
        if len(self.results) == 1:
            self.execute_selected_command()

    # Run
    def run(self, cmd=''):

        if not self.database and not self.database_exists:
            # No database at all, add the default one
            for command in DEFAULT_COMMANDS:
                self.add_database_entry(command)
        elif not self.database:
            # Empty database
            print("No database. Add commands with: xx -a [label] <command>")
            exit(1)

        self.ui.initialise_display()

        # If passed a search term, try to auto run it
        if cmd:
            self.ui.input.set_value(cmd)
            self.do_autorun()

        try:
            while True and cmd != '#AUTOEXIT#':
                self.ui.redraw()
                self.ui.get_input()
        finally:
            self.ui.finalise_display()

        if cmd == '#AUTOEXIT#':
            raise UnitTestException()
