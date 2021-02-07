import unittest
from xxcmd import DBItem


class DbItemTests(unittest.TestCase):

    def test_basic(self):
        item = DBItem('[label] command')
        self.assertEqual(item.label, 'label')
        self.assertEqual(item.cmd, 'command')

    def test_search_key(self):
        item = DBItem('[My Label] Some Command')
        self.assertEqual(item.search_key(), 'my label some command')

    def test_pretty(self):
        item = DBItem('[My Label] Some Command')

        # No ident
        self.assertEqual(item.pretty(0), 'My Label Some Command')

        # Indent
        self.assertEqual(item.pretty(10), 'My Label   Some Command')

        # No label
        self.assertEqual(item.pretty(10, False), 'Some Command')

    def test_parsing(self):

        # No label
        item = DBItem('no label here')
        self.assertTrue(not item.label)
        self.assertEqual(item.cmd, 'no label here')

        # Not a label
        item = DBItem('echo "[Not a label]"')
        self.assertTrue(not item.label)
        self.assertEqual(item.cmd, 'echo "[Not a label]"')

        # A label
        item = DBItem('echo "foo" [Echo It]')
        self.assertEqual(item.label, 'Echo It')
        self.assertEqual(item.cmd, 'echo "foo"')

        # Label at front
        item = DBItem('[Echo It] echo "foo"')
        self.assertEqual(item.label, 'Echo It')
        self.assertEqual(item.cmd, 'echo "foo"')

        # Bad label
        item = DBItem('echo "foo" Echo It]')
        self.assertEqual(item.label, '')
        self.assertEqual(item.cmd, 'echo "foo" Echo It]')

        # Only label
        item = DBItem('[Echo It]')
        self.assertEqual(item.label, 'Echo It')
        self.assertEqual(item.cmd, '')
