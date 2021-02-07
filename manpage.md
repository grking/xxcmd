% xx(1) | User Commands

NAME
====

xx - A helper for remembering useful shell commands.

SYNOPSIS
========

`xx [-h] [-a ...] [-t] [-l] [-v] [-i URL] [cmd]`

DESCRIPTION
===========

**xx** remembers shell commands, so you don't have to.

OPTIONS
=======

`-a ..., --add ...`

: Add the given command to the database. Command may begin
with a label enclosed in square brackets [label] <cmd>

`-h, --help`

: Show this help message and exit

`-i URL, --import-url URL`

: Import a command database from the given URL. Merge into existing database.

`-l, --list`

: Print all commands in the database

`-n, --no-echo`

: Don't echo the command to the terminal prior to execution.

`-t, --no-labels`

: Don't display command labels.

`-v, --version`

: Display program version.

EXAMPLES
========

`xx`

: Launch the interactive interface for searching and launching commands.

`xx -a ls -al`

: Adds the command "ls -al" to the command database.

`xx -a "[SSH Myhost] ssh -i ~/.ssh/secretkey.pem ubuntu@my-host.com"`

: Add the given SSH command with the label "SSH Myhost".

`xx host`

: Search for commands matching "host", if only one match is found, launch that command immediately.

`xx -i https://myhost.com/command-list.txt`

: Download and import the list of commands from the given URL.

FILES
=====

`~/.xxcmd`

: This is the file used to store commands.

BUGS
====

Please report bugs at https://github.com/grking/xxcmd/issues

AUTHOR
======

Written by Graham R King <grking.email@gmail.com>

SEE ALSO
========

appropos(1), history(1), man(1)
