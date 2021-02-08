import os
import unittest
import tempfile
import sys
from contextlib import contextmanager
import io
from .mockcurses import curses
import xxcmd
from xxcmd import CmdManager, DBItem, main

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

    def test_basic(self):
        xx = CmdManager()
        self.assertIsInstance(xx, CmdManager)

    def testfile(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'testdb')

    def get_xx(self):
        xx = CmdManager()
        xx.filename = self.testfile()
        return xx

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
        xx.import_database('file://' + self.testfile())

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
        self.assertTrue(xx.load_database())
        # Should have two lines
        self.assertEqual(len(xx.database), 2)
        self.assertEqual(
            xx.database[0].cmd, 'ssh -i ~/.ssh/key.pem me@myhost.com')

        # Test merge
        xx.filename = self.testfile() + '2'
        self.assertTrue(xx.load_database(True))
        # Should have four lines
        self.assertEqual(len(xx.database), 4)
        self.assertEqual(xx.database[2].cmd, 'ls -al')
        self.assertEqual(xx.database[2].label, 'My Command')

        # Test merge with passed data
        self.assertTrue(xx.load_database(True, [
            "top [Show Processes]",
            '[CPUs] cat /proc/cpuinfo | grep "model name" | sort | uniq -c'
        ]))
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
        xx.load_database()
        items = len(xx.database)

        # Add new entry with no save
        xx.add_database_entry('[New Entry] ps', True)
        self.assertEqual(len(xx.database), items + 1)
        self.assertEqual(xx.database[len(xx.database)-1].cmd, 'ps')

        # Add new entry as dbitem with no save
        newitem = DBItem('[Another Entry] ps aux')
        xx.add_database_entry(newitem, True)
        self.assertEqual(len(xx.database), items + 2)
        self.assertEqual(xx.database[len(xx.database)-1].cmd, 'ps aux')

        # Remove nothing
        xx.delete_database_entry(None, True)

        # Remove entry
        xx.delete_database_entry(xx.database[len(xx.database)-1], True)
        xx.delete_database_entry(xx.database[len(xx.database)-1], True)
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
        xx.load_database(False, [
            "one [My Label]",
            "[Your Label] two",
            "three"])
        xx.ui.input = 'one'
        xx.update_search()
        self.assertEqual(1, len(xx.results))
        xx.ui.input = 'label'
        xx.update_search()
        self.assertEqual(2, len(xx.results))
        self.assertEqual(xx.results[1].label, 'Your Label')

    def test_curses_redraw(self):
        xx = self.get_xx()
        xx.load_database()
        xx.update_search()
        xx.ui.initialise_display()
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
        xx.load_database()
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
        xx.load_database()
        xx.search_mode()
        xx.edit_mode()

    def test_import_from_remote_url(self):
        xx = self.get_xx()
        xx.filename = tempfile.mktemp()
        xx.import_database('https://pastebin.com/raw/zVxMGmRJ')

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
            result = xx.import_database('https://bad.domain.invalid')
        self.assertFalse(result)

    def test_print_all(self):
        xx = self.get_xx()
        xx.load_database()
        with captured_output() as (out, err):
            xx.print_commands()
        out.seek(0)
        for i, line in enumerate(out.read().strip().split(os.linesep)):
            newitem = DBItem(line)
            self.assertEqual(newitem.cmd, xx.database[i].cmd)

    def test_keys(self):
        xx = self.get_xx()
        xx.load_database()
        xx.filename = tempfile.mktemp()
        xx.update_search()

        # Test letter
        xx.ui.get_input('a')
        self.assertEqual(xx.ui.input, "a")

        # Test backspace
        xx.ui.get_input('\x08')
        self.assertEqual(xx.ui.input, "")
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
        self.assertEqual(xx.ui.input, "SSH Homea")
        # Test backspace
        xx.ui.get_input('\x08')
        self.assertEqual(xx.ui.input, "SSH Home")
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

        os.unlink(xx.filename)

    def test_autorun(self):
        xx = self.get_xx()
        xx.load_database()
        self.assertRaises(Exception, lambda: xx.run('#AUTOEXIT#'))

    def test_main(self):
        sys.argv = ['xx', '#AUTOEXIT#']
        self.assertRaises(Exception, lambda: main())
