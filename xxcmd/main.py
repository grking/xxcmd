# main.py
import argparse
import os
from .cmdmanager import CmdManager


__version__ = "0.9.1"


def main():

    # Create the parser and add arguments
    parser = argparse.ArgumentParser(
        prog='xx', description="Remembers other shell commands, "
        "so you don't have to.")

    parser.add_argument(
        '-a', '--add', nargs=argparse.REMAINDER,
        help='Add the given command to the database. Command may begin '
        'with a label enclosed in square brackets [label] <cmd>')

    parser.add_argument(
        '-b', '--no-border', action='store_const', const=True,
        help="Don't display a window border.")

    parser.add_argument(
        '-e', '--no-help', action='store_const', const=True,
        help="Don't display the shortcut key help footer.")

    parser.add_argument(
        '-i', '--import-url', nargs=1, metavar='URL',
        help="Import a command database from the given URL. Merge "
        "into existing database.")

    parser.add_argument(
        '-c', '--create-config', action='store_true',
        help="Create a config file in the users home directory if one "
        "doesn't already exist.")

    parser.add_argument(
        '-f', '--db-file', nargs=1, metavar='FILE',
        help="Use the command database file specified rather than "
        "the default.")

    parser.add_argument(
        '-g', '--no-global-database', action='store_const', const=True,
        help="Don't load the global system database.")

    # Hidden curses key test debug mode
    parser.add_argument(
        '--key-test', action='store_true', help=argparse.SUPPRESS)

    parser.add_argument(
        '-l', '--list', action='store_true',
        help="Print all commands in the database")

    parser.add_argument(
        '-m', '--no-commands', action='store_const', const=True,
        help="Don't show commands in interactive view.")

    parser.add_argument(
        '-n', '--no-echo', action='store_const', const=True,
        help="Don't echo the command to the terminal prior to execution.")

    parser.add_argument(
        '-p', '--label-padding', action='store', metavar='PADDING', type=int,
        help="Add extra padding between labels and commands.")

    parser.add_argument(
        '-s', '--search-all', action='store_const', const=True,
        help="Search both labels and commands. Default is to search only "
        "labels first, and only search in commands if searching for labels "
        "resulted in no search results.")

    parser.add_argument(
        '-t', '--no-labels', action='store_const', const=True,
        help="Don't display command labels.")

    parser.add_argument(
        '-v', '--version', action='store_true',
        help="Display program version.")

    parser.add_argument(
        'search', nargs='*', metavar='SEARCH',
        help="Search for a matching command and run it immediately.")

    # Parse and print the results
    args = parser.parse_args()

    if args.version:
        print("xx (xxcmd) {0}".format(__version__))
        exit(0)

    os.environ.setdefault('ESCDELAY', '1')

    # Create our SSH Manager
    manager = CmdManager()

    # Switch database file?
    if args.db_file:
        manager.filename = args.db_file[0]

    # Parse switches
    if args.no_labels:
        manager.config.show_labels = not args.no_labels
    if args.no_echo:
        manager.config.echo_commands = not args.no_echo
    if args.no_border:
        manager.config.draw_window_border = not args.no_border
    if args.no_help:
        manager.config.display_help_footer = not args.no_help
    if args.no_global_database:
        manager.config.load_global_database = not args.no_global_database
    if args.label_padding:
        manager.config.label_padding = args.label_padding
    if args.no_commands:
        manager.config.show_commands = not args.no_commands
    if args.search_all:
        manager.config.search_labels_only = False
        manager.config.search_labels_first = False

    # Key test?
    if args.key_test:  # pragma: no cover
        manager.ui.run_key_test()
        exit(0)

    # Load db
    manager.load_databases()

    if args.create_config:
        outfile = manager.config.save()
        if outfile:
            print("Config file created: {0}".format(outfile))
            exit(0)
        else:
            print("Config file already exists")
            exit(1)

    if args.import_url:
        if manager.import_database_url(args.import_url[0]):
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
    if type(args.search) is list:
        args.search = ' '.join(args.search)
    manager.run(args.search)
