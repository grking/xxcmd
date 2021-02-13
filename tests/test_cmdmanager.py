import os
import unittest
import tempfile
import sys
from contextlib import contextmanager
import io
from .mockcurses import curses
import xxcmd
from xxcmd import CmdManager, DBItem, main
from xxcmd.config import Config
from xxcmd.cmdmanager import UnitTestException

# Mock curses during unit testing
xxcmd.consoleui.curses = curses


@contextmanager
def captured_output():
    new_out, new_err = io.StringIO(), io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class CmdManagerTests(unittest.TestCase):

    def get_xx(self):
        xx = CmdManager()
        xx.filename = self.testfile()
        xx.config.sort_by_label = False
        xx.config.sort_by_command = False
        # Don't load global system database
        xx.config.load_global_database = False
        return xx

    def test_basic(self):
        xx = CmdManager()
        self.assertIsInstance(xx, CmdManager)

    def testfile(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'testdb')

    def test_load_file(self):
        xx = self.get_xx()
        data = xx.get_file_contents(self.testfile())

        # Should have two lines
        self.assertEqual(len(data), 2)

        # Should have no leading spaces
        self.assertFalse(data[1].startswith(' '))

        # Try non-existant file
        data = xx.get_file_contents('/invalid/path')
        self.assertFalse(data)

    def test_import_from_url(self):
        xx = self.get_xx()
        xx.import_database_url('file://' + self.testfile())

        data = xx.database

        # Should have two lines
        self.assertEqual(len(data), 2)

        # Should have no leading/trailing spaces
        self.assertFalse(data[1].cmd.startswith(' '))
        self.assertFalse(data[1].cmd.endswith(' '))
        self.assertFalse(data[1].label.startswith(' '))
        self.assertFalse(data[1].label.endswith(' '))

    def test_load_and_save_database(self):
        xx = self.get_xx()

        # Check default file load
        self.assertTrue(xx.load_databases())
        # Should have two lines
        self.assertEqual(len(xx.database), 2)
        self.assertEqual(
            xx.database[0].cmd, 'ssh -i ~/.ssh/key.pem me@myhost.com')

        # Test merge
        filename = self.testfile() + '2'
        self.assertTrue(xx.load_file(filename, True))
        # Should have four lines
        self.assertEqual(len(xx.database), 4)
        self.assertEqual(xx.database[2].cmd, 'ls -al')
        self.assertEqual(xx.database[2].label, 'My Command')

        # Test merge with passed data
        self.assertTrue(xx.load_data([
            "top [Show Processes]",
            '[CPUs] cat /proc/cpuinfo | grep "model name" | sort | uniq -c'
        ], True))
        # Should have six lines
        self.assertEqual(len(xx.database), 6)
        self.assertEqual(xx.database[4].cmd, 'top')
        self.assertEqual(xx.database[4].label, 'Show Processes')

        # Save it whilst we're here
        xx.filename = tempfile.mktemp()
        xx.save_database()
        data = xx.get_file_contents(xx.filename)
        os.unlink(xx.filename)
        self.assertEqual(6, len(data))
        self.assertEqual(
            data[5],
            'cat /proc/cpuinfo | grep "model name" | sort | uniq -c [CPUs]')

    def test_add_and_delete(self):
        xx = self.get_xx()
        xx.load_databases()
        items = len(xx.database)

        # Add new entry with no save
        xx.save_disabled = True
        xx.add_database_entry('[New Entry] ps')
        self.assertEqual(len(xx.database), items + 1)
        self.assertEqual(xx.database[len(xx.database)-1].cmd, 'ps')

        # Test dupe reject
        ok = xx.add_database_entry('[New Entry] ps')
        self.assertFalse(ok)

        # Add new entry as dbitem with no save
        newitem = DBItem('[Another Entry] ps aux')
        xx.add_database_entry(newitem)
        self.assertEqual(len(xx.database), items + 2)
        self.assertEqual(xx.database[len(xx.database)-1].cmd, 'ps aux')

        # Remove nothing
        xx.delete_database_entry(None)

        # Remove entry
        xx.delete_database_entry(xx.database[len(xx.database)-1])
        xx.delete_database_entry(xx.database[len(xx.database)-1])
        self.assertEqual(len(xx.database), items)
        self.assertEqual(
            xx.database[len(xx.database)-1].cmd,
            'du --max-depth-1 -h .')

    def test_curses_start_stop(self):
        xx = self.get_xx()
        xx.ui.initialise_display()
        xx.ui.finalise_display()

    def test_search(self):
        xx = self.get_xx()
        xx.load_data([
            "one [My Label]",
            "[Your Label] two",
            "three"], False)
        xx.ui.input.set_value('one')
        xx.update_search()
        self.assertEqual(1, len(xx.results))
        xx.ui.input.set_value('label')
        xx.update_search()
        self.assertEqual(2, len(xx.results))
        self.assertEqual(xx.results[1].label, 'Your Label')
        # Test search of labels only
        xx.config.search_labels_first = False
        xx.config.search_labels_only = True
        xx.ui.input.set_value('three')
        xx.update_search()
        self.assertEqual(len(xx.results), 0)

    def test_curses_redraw(self):
        xx = self.get_xx()
        xx.load_databases()
        xx.update_search()
        xx.ui.initialise_display()
        xx.config.bracket_labels = True
        xx.ui.redraw()
        xx.config.show_labels = False
        xx.ui.redraw()
        xx.config.show_commands = False
        xx.ui.redraw()
        xx.ui.finalise_display()

    def test_execute(self):
        xx = self.get_xx()
        xx.ui.initialise_display()
        # Execute nothing
        result = xx.execute_command(None, False)
        self.assertIsNone(result)
        # Execute something
        result = xx.execute_command(DBItem('echo foo'), False)
        self.assertEqual(result, 'foo')

    def test_selection(self):
        xx = self.get_xx()
        xx.load_databases()
        xx.update_search()
        items = len(xx.database)
        self.assertEqual(items, 2)
        xx.selection_up()
        self.assertEqual(xx.selected_row, 0)
        for i in range(5):
            xx.selection_down()
        self.assertEqual(xx.selected_row, 1)
        self.assertEqual(xx.selected_item.cmd, "du --max-depth-1 -h .")

    def test_mode_changing(self):
        xx = self.get_xx()
        xx.load_databases()
        xx.search_mode()
        xx.edit_label_mode()
        xx.search_mode()
        xx.edit_command_mode()
        xx.search_mode()
        xx.edit_newcmd_mode()
        xx.search_mode()
        # Mode changes with no search results
        xx.ui.input.set_value('abcdef98sdfsfHFHHHFh')
        xx.update_search()
        xx.edit_label_mode()
        xx.edit_command_mode()

    def test_import_from_remote_url(self):
        xx = self.get_xx()
        xx.filename = tempfile.mktemp()
        xx.import_database_url('https://pastebin.com/raw/zVxMGmRJ')

        data = xx.database

        # Should have two lines
        self.assertEqual(len(data), 2)

        # Should have no leading/trailing spaces
        self.assertFalse(data[1].cmd.startswith(' '))
        self.assertFalse(data[1].cmd.endswith(' '))
        self.assertFalse(data[1].label.startswith(' '))
        self.assertFalse(data[1].label.endswith(' '))
        # Last label
        self.assertEqual(data[1].label, "Show Processes")
        os.unlink(xx.filename)

    def test_import_from_remote_url_fail(self):
        xx = self.get_xx()
        with captured_output() as (out, err):
            result = xx.import_database_url('https://bad.domain.invalid')
        self.assertFalse(result)

    def test_print_all(self):
        xx = self.get_xx()
        xx.load_databases()
        with captured_output() as (out, err):
            xx.print_commands()
        out.seek(0)
        for i, line in enumerate(out.read().strip().split(os.linesep)):
            newitem = DBItem(line)
            self.assertEqual(newitem.cmd, xx.database[i].cmd)

        # with no labels
        xx.config.show_labels = False
        with captured_output() as (out, err):
            xx.print_commands()
        out.seek(0)
        for i, line in enumerate(out.read().strip().split(os.linesep)):
            newitem = DBItem(line)
            self.assertEqual(newitem.cmd, xx.database[i].cmd)

    def test_keys(self):
        xx = self.get_xx()
        xx.load_databases()
        xx.filename = tempfile.mktemp()
        xx.update_search()

        # Test letter
        xx.ui.get_input('a')
        self.assertEqual(xx.ui.input.value, "a")

        # Test backspace
        xx.ui.get_input('\x08')
        self.assertEqual(xx.ui.input.value, "")
        # Test down
        xx.ui.get_input('KEY_DOWN')
        self.assertEqual(xx.selected_row, 1)
        # Test delete
        xx.ui.get_input('KEY_DC')
        xx.update_search()
        self.assertEqual(xx.selected_row, 0)
        # Test up
        xx.ui.get_input('KEY_UP')
        self.assertEqual(xx.selected_row, 0)
        # Test ignore
        xx.ui.get_input('ignore me')

        # Test edit label
        xx.ui.get_input('KEY_F(1)')
        self.assertTrue('Edit' in xx.ui.input_prefix)

        # Test letter
        xx.ui.get_input('a')
        self.assertEqual(xx.ui.input.value, "SSH Homea")
        # Test backspace
        xx.ui.get_input('\x08')
        self.assertEqual(xx.ui.input.value, "SSH Home")
        # Test ignore
        xx.ui.get_input('ignore me')
        # Test return (save)
        xx.ui.get_input('\n')
        self.assertEqual(xx.mode, 'search')
        # Test edit label
        xx.ui.get_input('KEY_F(1)')
        self.assertEqual(xx.mode, 'edit')
        # Test escape
        xx.ui.get_input('\x1b')
        self.assertEqual(xx.mode, 'search')

        # Test left arrow
        xx.ui.input.set_value("hello and welcome")
        xx.ui.get_input('KEY_LEFT')
        self.assertEqual(xx.ui.input.cursor, 16)
        xx.ui.get_input('KEY_RIGHT')
        self.assertEqual(xx.ui.input.cursor, 17)
        xx.ui.get_input('KEY_HOME')
        self.assertEqual(xx.ui.input.cursor, 0)
        xx.ui.get_input('KEY_END')
        self.assertEqual(xx.ui.input.cursor, 17)
        xx.ui.get_input('kLFT5')
        self.assertEqual(xx.ui.input.cursor, 10)
        xx.ui.get_input('KEY_HOME')
        xx.ui.get_input('kRIT5')
        self.assertEqual(xx.ui.input.cursor, 6)

        os.unlink(xx.filename)

    def test_autorun(self):
        xx = self.get_xx()
        xx.load_databases()
        self.assertRaises(UnitTestException, lambda: xx.run('#AUTOEXIT#'))

    def test_no_database(self):
        xx = self.get_xx()
        xx.filename = '/tmp/nodatabase'
        xx.save_disabled = True
        xx.load_databases()
        self.assertRaises(UnitTestException, lambda: xx.run('#AUTOEXIT#'))

    def test_main(self):
        sys.argv = ['xx', '-v']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '#AUTOEXIT#']
        self.assertRaises(Exception, lambda: main())
        sys.argv = ['xx', '-tmnsbp1', '#AUTOEXIT#']
        self.assertRaises(Exception, lambda: main())

        configfile = tempfile.mktemp()
        Config.DEFAULT_CONFIG_FILE = configfile
        sys.argv = ['xx', '-c']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '-c']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '-l']
        self.assertRaises(SystemExit, lambda: main())
        os.unlink(configfile)

        dbfile = tempfile.mktemp()
        sys.argv = ['xx', '-f', dbfile, '-i',
                    'https://pastebin.com/raw/zVxMGmRJ']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '-f', dbfile, '-i', 'https://invalid']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '-f', dbfile, '-a', '[New] command']
        self.assertRaises(SystemExit, lambda: main())
        sys.argv = ['xx', '-f', dbfile, '-a', '[New] command']
        self.assertRaises(SystemExit, lambda: main())
        os.unlink(dbfile)

    def test_sorting(self):
        xx = self.get_xx()
        xx.load_data([
            "One [My Label]",
            "[Your Label] Two",
            "[Op] Bash",
            "[Op2] apple",
            "[Alpha] Four",
            "[adam] nine",
            "three"], False)
        # Default natural sort
        xx.update_search()
        self.assertEqual(xx.results[0].cmd, 'One')
        # Label sort
        xx.config.sort_by_label = True
        xx.update_search()
        self.assertEqual(xx.results[1].label, 'Alpha')
        # Command sort
        xx.config.sort_by_label = False
        xx.config.sort_by_command = True
        xx.update_search()
        self.assertEqual(xx.results[0].cmd, 'Bash')
        # Label sort - case insensitive
        xx.config.sort_by_label = True
        xx.config.sort_by_command = False
        xx.config.sort_case_sensitive = False
        xx.update_search()
        self.assertEqual(xx.results[1].label, 'adam')
        # Command sort - case insensitive
        xx.config.sort_by_label = False
        xx.config.sort_by_command = True
        xx.config.sort_case_sensitive = False
        xx.update_search()
        self.assertEqual(xx.results[0].cmd, 'apple')

    def test_editing(self):
        xx = self.get_xx()
        xx.load_data([
            '[My Label] My command',
            '[Another Label] Another command'
        ], False)
        xx.filename = tempfile.mktemp()
        xx.update_search()
        # Label edit
        xx.ui.input.set_value('New Label')
        xx.update_selected_label()
        self.assertEqual(xx.database[0].label, 'New Label')
        # Command edit
        xx.ui.input.set_value('New Command')
        xx.update_selected_command()
        self.assertEqual(xx.database[0].cmd, 'New Command')

        os.unlink(xx.filename)

    def test_flash(self):
        xx = self.get_xx()
        xx.ui.initialise_display()
        xx.ui.flash("Test")
