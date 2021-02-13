# consoleui.py
import os
import curses
from curses.ascii import isprint
import time
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
        # Default locations of things
        self.prompt_pos = {'x': 1, 'y': 1}
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
        # Result window region
        self.cmd_region = {
            'minx': 0,
            'miny': 0,
            'maxx': self.win_width-1,
            'maxy': self.win_height-1
        }
        # Default help footer text
        self.help_row = ("Return:Run  F1:Edit Label  "
            "F2:Edit Cmd  F3:Add New  Del:Delete")

    # Initialise our display
    def initialise_display(self):
        # Update some options from our latest runtime config
        if not self.parent.config.draw_window_border:
            self.prompt_pos = {'x': 0, 'y': 0}
        self.win = curses.initscr()
        curses.noecho()
        self.win.keypad(True)
        curses.cbreak()
        curses.curs_set(1)
        self.resize()

    # Finalise our display
    def finalise_display(self):
        curses.nocbreak()
        curses.echo()
        self.win.keypad(False)
        curses.endwin()
        self.win = None

    # Recalculate window regions
    def resize(self):
        # Get the latest window size
        self.win_height, self.win_width = self.win.getmaxyx()
        # Default the entire screen
        self.cmd_region = {
            'minx': 0,
            'miny': 1,
            'maxx': self.win_width-1,
            'maxy': self.win_height-1,
        }
        # Adjust if window border
        if self.parent.config.draw_window_border:
            self.cmd_region['minx'] += 1
            self.cmd_region['miny'] += 2
            self.cmd_region['maxx'] -= 1
            self.cmd_region['maxy'] -= 1
        # Adjust if help footer
        if self.parent.config.display_help_footer:
            self.cmd_region['maxy'] -= 1

    # Print some text
    def print_at(self, y, x, text, attrib=curses.A_NORMAL):
        # Get the latest window size
        self.resize()
        # Really, really small term?
        if self.win_width <= 2 or self.win_height <= 2:
            return
        # Text out of the term totally?
        if y < 0 or y >= self.win_height or x < 0 or x >= self.win_width-1:
            return
        # Plot the text
        text = text[:self.win_width - (x+1)]
        self.win.addstr(y, x, text, attrib)

    # Print a line of text
    def print_line_at(self, y, x, text, attrib=curses.A_NORMAL):
        self.print_at(y, x, text, attrib)
        self.win.clrtoeol()

    # Draw a horizontal line
    def hline(self, y):
        # Get the latest window size
        self.resize()
        # Really, really small term?
        if self.win_width <= 2 or self.win_height <= 3:
            return
        self.win.hline(2, 1, curses.ACS_HLINE, self.win_width-2)
        self.win.addch(2, 0, curses.ACS_LTEE)
        self.win.addch(2, self.win_width-1, curses.ACS_RTEE)

    # Term row to array index
    def termrow_to_idx(self, row):
        return (row + self.row_offset) - self.cmd_region['miny']

    # Flash a brief message
    def flash(self, message):
        self.print_line_at(self.prompt_pos['y'], self.prompt_pos['x'], message)
        self.win.refresh()
        time.sleep(1)

    # Update our window output
    def redraw(self):

        # Calculate row offset for scrolling
        self.row_offset = self.parent.selected_row - (
            self.cmd_region['maxy'] - self.cmd_region['miny'])
        if self.row_offset < 0:
            self.row_offset = 0

        # Calculate column offset for scrolling
        self.col_offset = self.input.cursor - (
            self.win_width - (self.cmd_region['minx'] + 2 + len(self.input_prefix)))
        if self.col_offset < 0:
            self.col_offset = 0

        # Print the input line
        line = self.input.value
        line = line[self.col_offset:]
        self.print_line_at(
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
        y = self.cmd_region['miny']
        last_row = self.cmd_region['maxy']
        while y <= last_row:

            idx = self.termrow_to_idx(y)
            attrib = curses.A_NORMAL

            # Highlight selected row
            if idx == self.parent.selected_row:
                attrib = curses.A_REVERSE

            # Print search results for as long as we have them
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
                    self.print_line_at(
                        y, self.cmd_region['minx'], label.ljust(indent), attrib)
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
                        self.win_width - indent - self.cmd_region['minx'])
                self.print_line_at(
                    y, self.cmd_region['minx'] + indent, cmd, attrib)

            else:
                # Fill the rest of the space with blank lines
                self.print_line_at(y, self.cmd_region['minx'], "", attrib)

            y += 1

        # Display help footer
        if self.parent.config.display_help_footer:
            footer = self.help_row
            helprow = self.cmd_region['maxy'] + 1
            footer = footer.rjust(self.cmd_region['maxx'] - self.cmd_region['minx'])
            self.print_line_at(
                helprow, self.cmd_region['minx'], footer)

        # Draw lines for boxes
        if self.parent.config.draw_window_border:
            self.win.box()
            self.hline(2)

        # Move visual cursor
        curx = len(self.input_prefix) + (
            (self.input.cursor + self.prompt_pos['x']) - self.col_offset)
        if curx < self.win_width:
            self.win.move(self.prompt_pos['y'], curx)

        self.win.refresh()

    # Get input
    def get_input(self, key=None):

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
        # Add printable ascii characters to our input
        elif len(key) == 1 and isprint(key):
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
