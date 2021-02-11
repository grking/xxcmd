# lineedit.py
# A helper for editing a line of text


class LineEdit():

    # Constants for cursor movement step
    CHARACTER = 0
    LINE = 1
    WORD = 2

    @property
    def value(self):
        return self._linetext

    @property
    def cursor(self):
        return self._cursor_pos

    def __init__(self):
        self.clear()

    # Clear everything
    def clear(self):
        self._linetext = ''
        self._history = []
        self._cursor_default()

    # Set our entire line text as a string
    def set_value(self, value, use_history=True):
        # Remember the current value
        self._history.append(self._linetext)
        if len(self._history) > 20:
            self._history = self._history[1:]
        # Set the new value
        self._linetext = value
        # Set cursor
        self._cursor_default()

    # Restore a previous input line
    def pop_value(self):
        if self._history:
            self.set_value(self._history.pop(), False)
        else:
            self.clear()

    # Set the default cursor position
    def _cursor_default(self):
        # Default cursor position
        self._cursor_pos = len(self._linetext)

    # String representation
    def __str__(self):
        return self._linetext

    # Add a character to our line data at current cursor position
    def addchar(self, value):
        if len(value) > 1:
            raise Exception(
                'Expected one character input not "{0}"'.format(value))
        self._linetext = (self._linetext[:self._cursor_pos] +
                          value + self._linetext[self._cursor_pos:])
        self._cursor_pos += 1

    # Delete a character from our line from the current cursor position
    def delchar(self):
        # We can't delete from nothing
        if not self._linetext:
            return
        self._linetext = self._linetext[:self._cursor_pos -
                                        1] + self._linetext[self._cursor_pos:]
        self._cursor_pos -= 1

    # Move cursor left
    def left(self, step=0):
        if step == LineEdit.CHARACTER:
            self._cursor_pos -= 1
        elif step == LineEdit.LINE:
            self._cursor_pos = 0
        elif step == LineEdit.WORD:
            # Move to start of next word, backwards
            foundchar = False
            while True:
                self._cursor_pos -= 1
                if self._cursor_pos < 0:
                    break
                if self._linetext[self._cursor_pos] != ' ':
                    foundchar = True
                if foundchar and self._linetext[self._cursor_pos] == ' ':
                    self._cursor_pos += 1
                    break

        if self._cursor_pos < 0:
            self._cursor_pos = 0

    # Move cursor right
    def right(self, step=0):
        if step == LineEdit.CHARACTER:
            self._cursor_pos += 1
        elif step == LineEdit.LINE:
            self._cursor_pos = len(self._linetext)
        elif step == LineEdit.WORD:
            # Move to start of next word
            foundspace = False
            while True:
                self._cursor_pos += 1
                if self._cursor_pos >= len(self._linetext):
                    break
                if self._linetext[self._cursor_pos] == ' ':
                    foundspace = True
                if foundspace and self._linetext[self._cursor_pos] != ' ':
                    break

        if self._cursor_pos > len(self._linetext):
            self._cursor_pos = len(self._linetext)
