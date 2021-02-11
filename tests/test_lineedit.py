import unittest
from xxcmd.lineedit import LineEdit


class LineEditTests(unittest.TestCase):

    def test_basic(self):
        edit = LineEdit()
        self.assertIsInstance(edit, LineEdit)

    def test_set_text(self):
        edit = LineEdit()
        edit.set_value('hello')
        self.assertEqual(edit.value, 'hello')

    def test_add_remove(self):
        edit = LineEdit()
        edit.addchar('a')
        edit.addchar('b')
        edit.addchar('c')
        edit.delchar()
        self.assertEqual(edit.value, 'ab')
        self.assertEqual(str(edit), 'ab')
        edit.delchar()
        edit.delchar()
        edit.delchar()
        self.assertEqual(str(edit), '')

    def test_invalid_add(self):
        edit = LineEdit()
        self.assertRaises(Exception, lambda: edit.addchar('ab'))

    def test_history(self):
        edit = LineEdit()
        edit.set_value('foo')
        edit.set_value('bar')
        edit.pop_value()
        self.assertEqual(edit.value, 'foo')
        for i in range(100):
            edit.set_value("value {0}".format(i))
        self.assertEqual(len(edit._history), 20)

    def test_cursor_editing(self):
        edit = LineEdit()
        self.assertEqual(edit.cursor, 0)
        edit.set_value('test')
        edit.left()
        edit.left()
        edit.left()
        edit.left()
        edit.left()
        edit.addchar('r')
        edit.addchar('e')
        self.assertEqual(str(edit), 'retest')
        edit.right()
        edit.addchar('r')
        edit.right()
        edit.right()
        edit.delchar()
        edit.addchar('a')
        self.assertEqual(str(edit), 'retreat')
        edit.right()
        edit.right()
        edit.right()
        edit.right()
        edit.addchar('!')
        self.assertEqual(str(edit), 'retreat!')
        self.assertEqual(edit.cursor, 8)

    def test_cursor_steps(self):
        edit = LineEdit()
        edit.set_value('hello')
        edit.left(LineEdit.LINE)
        self.assertEqual(edit.cursor, 0)
        edit.right(LineEdit.LINE)
        self.assertEqual(edit.cursor, 5)

        edit.set_value('one two three    four five    ')
        edit.left(LineEdit.WORD)
        edit.left(LineEdit.WORD)
        edit.left(LineEdit.WORD)
        edit.addchar('X')
        self.assertEqual(str(edit), 'one two Xthree    four five    ')
        edit.left(LineEdit.WORD)
        edit.left(LineEdit.WORD)
        edit.left(LineEdit.WORD)
        edit.addchar('X')
        self.assertEqual(str(edit), 'Xone two Xthree    four five    ')
        edit.delchar()
        self.assertEqual(str(edit), 'one two Xthree    four five    ')

        edit.right(LineEdit.WORD)
        edit.right(LineEdit.WORD)
        edit.addchar('Y')
        self.assertEqual(str(edit), 'one two YXthree    four five    ')
        edit.right(LineEdit.WORD)
        edit.right(LineEdit.WORD)
        edit.addchar('X')
        self.assertEqual(str(edit), 'one two YXthree    four Xfive    ')
        edit.right(LineEdit.WORD)
        edit.right(LineEdit.WORD)
        edit.addchar('X')
        self.assertEqual(str(edit), 'one two YXthree    four Xfive    X')
