# dbitem.py
import re


class DBItem():

    # Auto detect and split labels/cmd
    def __init__(self, line):
        label = ""
        post = re.match(r'.*(\[(.*)\])$', line)
        pre = re.match(r'^(\[(.*)\])(.*)$', line)
        if post:
            label = post.group(2)
            line = re.sub(r'(\[(.*)\])$', '', line)
        elif pre:
            label = pre.group(2)
            line = re.sub(r'^(\[(.*)\])', '', line)
        self.label = label.strip()
        self.cmd = line.strip()

    # Return a string suitable for substring searching
    def search_key(self):
        return f"{self.label} {self.cmd}".lower()

    # Return a pretty string representation
    def pretty(self, indent=0, show_label=True):

        if self.label and show_label:
            label = self.label.ljust(indent) + " "
        else:
            label = ""

        return f"{label}{self.cmd}"
