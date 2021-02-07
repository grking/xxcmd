import os
import unittest
import tempfile
from xxcmd import CmdManager, DBItem


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
        self.assertEqual(6, len(data))
        self.assertEqual(
            data[5],
            'cat /proc/cpuinfo | grep "model name" | sort | uniq -c [CPUs]')

    def test_add_and_delete(self):
        xx = self.get_xx()
        xx.load_database()
        xx.filename = tempfile.mktemp()
        items = len(xx.database)

        # Add new entry with no save
        xx.add_database_entry('[New Entry] ps', True)
        self.assertEqual(len(xx.database), items + 1)
        self.assertEqual(xx.database[len(xx.database)-1].cmd, 'ps')

        # Remove entry
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
        xx.initialise_display()
        xx.redraw()
        xx.finalise_display()

    def test_execute(self):
        xx = self.get_xx()
        xx.initialise_display()
        result = xx.execute_command(DBItem('echo "foo"'), False)
        self.assertEqual(result, 'foo')
