import os
import unittest
import tempfile
import sys
from contextlib import contextmanager
import io
from xxcmd import CmdManager, DBItem, main


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
        xx.initialise_display()
        xx.finalise_display()

    def test_search(self):
        xx = self.get_xx()
        xx.load_database(False, [
            "one [My Label]",
            "[Your Label] two",
            "three"])
        xx.search = 'one'
        xx.update_search()
        self.assertEqual(1, len(xx.results))
        xx.search = 'label'
        xx.update_search()
        self.assertEqual(2, len(xx.results))
        self.assertEqual(xx.results[1].label, 'Your Label')

    def test_curses_redraw(self):
        xx = self.get_xx()
        xx.load_database()
        xx.update_search()
        xx.initialise_display()
        xx.redraw()
        xx.mode = CmdManager.MODE_EDIT_LABEL
        xx.redraw()
        xx.finalise_display()

    def test_execute(self):
        xx = self.get_xx()
        xx.initialise_display()
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
        xx.selected_row = -1
        self.assertEqual(xx.selected_row, 1)
        xx.selected_row = 100
        self.assertEqual(xx.selected_row, 2)
        self.assertEqual(xx.selected_item.cmd, "du --max-depth-1 -h .")

    def test_mode_changing(self):
        xx = self.get_xx()
        xx.load_database()
        xx.mode = CmdManager.MODE_EDIT_LABEL
        xx.update_search()

        xx.mode = CmdManager.MODE_EDIT_LABEL
        xx.selected_row = 1
        xx.mode = CmdManager.MODE_EDIT_LABEL
        xx.mode = CmdManager.MODE_NORMAL

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
        xx.get_input('a')
        self.assertEqual(xx.search, "a")

        # Test backspace
        xx.get_input('\x08')
        self.assertEqual(xx.search, "")
        # Test down
        xx.get_input('KEY_DOWN')
        self.assertEqual(xx.selected_row, 2)
        # Test delete
        xx.get_input('KEY_DC')
        xx.update_search()
        self.assertEqual(xx.selected_row, 1)
        # Test up
        xx.get_input('KEY_UP')
        self.assertEqual(xx.selected_row, 1)
        # Test ignore
        xx.get_input('ignore me')

        # Test edit label
        xx.get_input('KEY_F(1)')
        self.assertEqual(xx.mode, CmdManager.MODE_EDIT_LABEL)

        # Test letter
        xx.get_input('a')
        self.assertEqual(xx.edit, "SSH Homea")
        # Test backspace
        xx.get_input('\x08')
        self.assertEqual(xx.edit, "SSH Home")
        # Test ignore
        xx.get_input('ignore me')
        # Test return (save)
        xx.get_input('\n')
        self.assertEqual(xx.mode, CmdManager.MODE_NORMAL)
        # Test edit label
        xx.get_input('KEY_F(1)')
        self.assertEqual(xx.mode, CmdManager.MODE_EDIT_LABEL)
        # Test escape
        xx.get_input('\x1b')
        self.assertEqual(xx.mode, CmdManager.MODE_NORMAL)

        os.unlink(xx.filename)

    def test_autorun(self):
        xx = self.get_xx()
        xx.load_database()
        self.assertRaises(Exception, lambda: xx.run('#AUTOEXIT#'))

    def test_main(self):
        sys.argv = ['xx', '#AUTOEXIT#']
        self.assertRaises(Exception, lambda: main())
