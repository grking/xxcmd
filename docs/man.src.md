% xx(1) | User Commands

# NAME

**xx** - A helper for remembering useful shell commands.

# SYNOPSIS

**xx** `[-h] [-a ...] [-i URL] [-c] [-l] [-m] [-n] [-p PADDING] [-s] [-t] [-b] [-v] [cmd]`

# DESCRIPTION

**xx** remembers shell commands, so you don't have to.

# OPTIONS

(generated automatically by build.py)

# EXAMPLES

`xx`

: Launch the interactive interface for searching and launching commands.

`xx -a ls -al`

: Adds the command "ls -al" to the command database.

`xx -a [SSH Myhost] ssh -i ~/.ssh/secretkey.pem ubuntu@my-host.com`

: Add the given SSH command with the label "SSH Myhost".

`xx host`

: Search for commands matching "host", if only one match is found, launch that command immediately.

`xx -i https://myhost.com/command-list.txt`

: Download and import the list of commands from the given URL.

# FILES

`~/.xxcmd`

: This is the file used to store the database of commands.

`~/.xxcmdrc`

: An optional configuration file.

# BUGS

Please report bugs at https://github.com/grking/xxcmd/issues

# AUTHOR

Written by Graham R King <grking.email@gmail.com>

# SEE ALSO

appropos(1), history(1), man(1)
