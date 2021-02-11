# consoleui.py
import os
import curses
from .lineedit import LineEdit


# Curses UI for our application
class ConsoleUI():

    def __init__(self, parent):
        # Our parent
        self.parent = parent
        # Our curses window
        self.win = None
        # And dimensions of it
        self.win_width = 0
        self.win_height = 0
        # Locations of things
        self.prompt_pos = {'x': 1, 'y': 1}
        self.commands_pos = {'x': 1, 'y': 2}
        # Input line edit
        self.input = LineEdit()
        # Input line prefix
        self.input_prefix = ''
        # Key press event handlers
        self.key_events = {}
        # Offset for scrolling through the list
        self.row_offset = 1
        # Offset for editing long lines
        self.col_offset = 1

    # Initialise our display
    def initialise_display(self):
        self.win = curses.initscr()
        curses.noecho()
        self.win.keypad(True)
        curses.cbreak()
        curses.curs_set(1)
        self.win_height, self.win_width = self.win.getmaxyx()

    # Finalise our display
    def finalise_display(self):
        curses.nocbreak()
        curses.echo()
        self.win.keypad(False)
        curses.endwin()
        self.win = None

    # Print some text
    def print_at(self, y, x, text, attrib=curses.A_NORMAL):
        # Get the latest window size
        self.win_height, self.win_width = self.win.getmaxyx()
        # Really, really small term?
        if self.win_width <= 2 or self.win_height <= 2:
            return
        # Text out of the term totally?
        if y < 0 or y >= self.win_height-1 or x < 0 or x >= self.win_width-1:
            return
        # Plot the text
        text = text[:self.win_width - (x+1)]
        self.win.addstr(y, x, text, attrib)
        self.win.clrtoeol()

    # Term row to array index
    def termrow_to_idx(self, row):
        return (row + self.row_offset) - self.commands_pos['y']

    # Update our window output
    def redraw(self):

        # Calculate row offset for scrolling
        self.row_offset = self.parent.selected_row - (
            self.win_height - (self.commands_pos['y'] + 2))
        if self.row_offset < 0:
            self.row_offset = 0

        # Calculate column offset for scrolling
        self.col_offset = self.input.cursor - (
            self.win_width - (self.commands_pos['x'] + 2 + len(self.input_prefix)))
        if self.col_offset < 0:
            self.col_offset = 0

        # Print the input line
        line = self.input.value
        line = line[self.col_offset:]
        self.print_at(
            self.prompt_pos['y'], self.prompt_pos['x'],
            "{0}{1}".format(self.input_prefix, line))

        # Determine max label length for indenting
        indent = 0
        if self.parent.config.align_commands:
            for item in self.parent.results:
                if len(item.label) > indent:
                    indent = len(item.label)
            indent += self.parent.config.label_padding
            if self.parent.config.bracket_labels:
                indent += 1

        # Display current search results
        y = self.commands_pos['y']
        while y < self.win_height-1:

            idx = self.termrow_to_idx(y)
            attrib = curses.A_NORMAL

            # Highlight selected row
            if idx == self.parent.selected_row:
                attrib = curses.A_REVERSE

            # Print search results for as long as we have then
            if idx < len(self.parent.results):
                item = self.parent.results[idx]
                label = ''

                # Showing labels?
                if self.parent.config.show_labels:
                    label = item.label
                    # Adding square bracket to labels?
                    if self.parent.config.bracket_labels:
                        label = "[{0}]".format(label)
                    # Bold labels?
                    if self.parent.config.bold_labels:
                        if attrib == curses.A_NORMAL:
                            attrib = curses.A_BOLD
                    # Print label
                    self.print_at(
                        y, self.commands_pos['x'], label.ljust(indent), attrib)
                    # Reset text attributes
                    if attrib == curses.A_BOLD:
                        attrib = curses.A_NORMAL

                # not showing labels...
                else:
                    indent = 0

                # Print command
                if self.parent.config.show_commands:
                    cmd = item.cmd
                else:
                    cmd = ''
                if self.parent.config.whole_line_selection:
                    cmd = cmd.ljust(
                        self.win_width - indent - self.commands_pos['x'])
                self.print_at(
                    y, self.commands_pos['x'] + indent, cmd, attrib)

            else:
                # Fill the rest of the space with blank lines
                self.print_at(y, self.commands_pos['x'], "", attrib)

            y += 1

        # Move visual cursor
        curx = len(self.input_prefix) + (
            (self.input.cursor + self.prompt_pos['x']) - self.col_offset)
        if curx < self.win_width:
            self.win.move(self.prompt_pos['y'], curx)

        if self.parent.config.draw_window_border:
            self.win.box()

        self.win.refresh()

    # Get input
    def get_input(self, key=None):

        # Bail out if testing
        if self.input.value == '#AUTOEXIT#':
            raise Exception("End Test")

        # Remember our starting mode
        mode = self.parent.mode

        try:
            # Get a key press if we weren't passed one
            if not key:    # pragma: no cover
                key = self.win.getkey()
        except KeyboardInterrupt:    # pragma: no cover
            exit(0)

        # Support backspace
        if key == '\x08' or key == 'KEY_BACKSPACE' or key == '\x7f':
            self.input.delchar()
        # Cursor movements
        elif key == 'KEY_LEFT':
            self.input.left()
        elif key == 'KEY_RIGHT':
            self.input.right()
        elif key == 'KEY_HOME' or key == 'kHOM5':
            self.input.left(self.input.LINE)
        elif key == 'KEY_END' or key == 'kEND5':
            self.input.right(self.input.LINE)
        elif key == 'kLFT5':
            self.input.left(self.input.WORD)
        elif key == 'kRIT5':
            self.input.right(self.input.WORD)
        # Check for key press event handler
        elif key in self.key_events.keys():
            self.key_events[key]()
        # Ignore strange stuff
        elif len(key) > 1:
            pass
        # Just record the key press
        else:
            self.input.addchar(key)

        # Trigger other event handlers

        # Don't trigger "always" events if mode changed
        if 'ALWAYS' in self.key_events.keys() and mode == self.parent.mode:
            self.key_events['ALWAYS']()

        return key

    # Display what curses sees when keys are pressed
    # Useful only for debugging terminal key press data
    def run_key_test(self):  # pragma: no cover
        try:
            self.initialise_display()
            y = 1
            self.win.addstr(0, 0, "Terminal type: " + os.environ['TERM'])
            while True:

                key = self.win.getkey()
                info = "'{0}' (0x{1})".format(key, key.encode().hex())
                self.win.addstr(y, 0, info)
                y += 1

                if y >= self.win_height-1:
                    self.win.clear()
                    y = 0

        finally:
            self.finalise_display()
