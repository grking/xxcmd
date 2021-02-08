"""A helper for remembering useful shell commands."""
import argparse
import os
from .cmdmanager import CmdManager
from .dbitem import DBItem

__all__ = ('DBItem', 'CmdManager')


__version__ = "0.4.0"


def main():

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(
        prog='xx', description="A helper for remembering useful shell "
        "commands. Type to interactively search, use UP and DOWN "
        "arrows to select, RETURN to launch the selected command. "
        "Use DELETE to remove the currently selected row. F1 or "
        "CTRL+E to edit the label of the selected item.")

    parser.add_argument(
        '-a', '--add', nargs=argparse.REMAINDER,
        help='Add the given command to the database. Command may begin '
        'with a label enclosed in square brackets [label] <cmd>')

    parser.add_argument(
        '-i', '--import-url', nargs=1, metavar='URL',
        help="Import a command database from the given URL. Merge "
        "into existing database.")

    parser.add_argument(
        '-l', '--list', action='store_true',
        help="Print all commands in the database")

    parser.add_argument(
        '-n', '--no-echo', action='store_true',
        help="Don't echo the command to the terminal prior to execution.")

    parser.add_argument(
        '-t', '--no-labels', action='store_true',
        help="Don't display command labels.")

    parser.add_argument(
        '-v', '--version', action='store_true',
        help="Display program version.")

    parser.add_argument(
        'cmd', nargs='?',
        help="Search for a matching command and run it immediately.")

    # Parse and print the results
    args = parser.parse_args()

    if args.version:
        print("xx (xxcmd) {0}".format(__version__))
        exit(0)

    os.environ.setdefault('ESCDELAY', '1')

    # Create our SSH Manager
    manager = CmdManager()
    manager.show_labels = not args.no_labels
    manager.no_echo = args.no_echo
    manager.load_database()

    if args.import_url:
        if manager.import_database(args.import_url[0]):
            print("Loaded data from URL")
            exit(0)
        else:
            exit(1)

    if args.add:
        if manager.add_database_entry(" ".join(args.add)):
            print("Added command.")
            exit(0)
        else:
            print("Duplicate command not added.")
            exit(1)

    if args.list:
        manager.print_commands()
        exit(0)

    # Run the command manager UI
    manager.run(args.cmd)
