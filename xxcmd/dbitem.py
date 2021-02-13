# dbitem.py
import re


class DBItem():

    # Auto detect and split labels/cmd
    def __init__(self, line, tags=None):
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
        if tags:
            self.tags = tags[:]
        else:
            self.tags = []

    # Return a string suitable for substring searching
    def search_key(self):
        return "{0} {1}".format(self.label, self.cmd).lower()
