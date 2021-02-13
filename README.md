# xxcmd

![](https://img.shields.io/pypi/pyversions/xxcmd) ![](https://img.shields.io/github/workflow/status/grking/xxcmd/Python%20Build) ![](https://img.shields.io/pypi/v/xxcmd) ![](https://img.shields.io/github/commits-since/grking/xxcmd/v0.9.0)

`xx` is a Linux shell command. `xx` remembers other shell commands, so you don't have to.

# Installation

## pip

Requires Python 3. Installation is simple using `pip`.

```bash
pip install xxcmd
```

Or `pip3` on Ubuntu or Debian based distros.

If typing `xx` at a command prompt gives you "Command not found", you likely don't have `~/.local/bin` on your PATH. Either install globally with `sudo pip install xxcmd` or add `~/.local/bin` to your PATH.

## Arch Linux

The `xxcmd` package in availabe in the AUR.

# Basic Usage Examples

Using `xx` you build up a database of useful commands and search and execute them whenever you like.

## Adding Command Examples

Most basic example, adding the `top` command.

```bash
xx -a top
```

Add the `du` command to display size of all files and directories in the current directory.

```bash
xx -a du --max-depth=1 -h .
```

Add the same command but with a friendly (searchable) label:

```bash
xx -a [File Sizes] du --max-depth=1 -h .
```

Adding our favourite ssh command:

```bash
xx -a [SSH Best Host] ssh -i ~/.ssh/mykey.pem me@myhost.com
```

Add the last command you executed:

```bash
xx -a !!
```

Add the last command you executed with a descriptive label:

```bash
xx -a [My Cool Label] !!
```

If adding commands containing characters that are interpreted by your shell, such as `|` or `&&` enclose the command in quotes. You can also use double quotes with bash's last command operator:

```bash
xx -a [Command with Pipes] "!!"
```


## Browse and Search Commands Interactively

Run `xx` with no options to enter the interactive view.

```bash
xx
```

## Quick Search and Execute

`xx` can search for matching commands and if only one match is found it will be immediately executed.

The search looks in labels and commands.

So one way to execute the `du` command we added above is:

```bash
xx sizes
```

Which finds a match on our label "File Sizes" and runs the associated command.

We could immediately ssh connect with:

```bash
xx best
```

Which would match our label "SSH Best Host".

# Interactive View

Invoking `xx` without options will open the interactive view. This presents a list of all commands with an interactive search.

Keys:

* <kbd>Up</kbd>/<kbd>Down</kbd> - navigate the list of commands.
* <kbd>Delete</kbd> - remove the currently selected command
* <kbd>Return</kbd> - execute the currently selected command
* <kbd>Escape</kbd> - exit
* <kbd>F1</kbd> or <kbd>CTRL+E</kbd> - Edit the label of the currently selected item
* <kbd>F2</kbd> or <kbd>CTRL+I</kbd> - Edit the label of the currently selected item
* <kbd>F3</kbd> or <kbd>CTRL+G</kbd> - Add a new command.
* Any other key press is added to the interactive search to filter the command list.

# Further Usage

```text
usage: xx [-h] [-a ...] [-b] [-e] [-i URL] [-c] [-f FILE] [-g] [-l] [-m] [-n]
          [-p PADDING] [-s] [-t] [-v]
          [SEARCH ...]

Remembers other shell commands, so you don't have to.

positional arguments:
  SEARCH                Search for a matching command and run it immediately.

optional arguments:
  -h, --help            show this help message and exit
  -a ..., --add ...     Add the given command to the database. Command may
                        begin with a label enclosed in square brackets [label]
                        <cmd>
  -b, --no-border       Don't display a window border.
  -e, --no-help         Don't display the shortcut key help footer.
  -i URL, --import-url URL
                        Import a command database from the given URL. Merge
                        into existing database.
  -c, --create-config   Create a config file in the users home directory if
                        one doesn't already exist.
  -f FILE, --db-file FILE
                        Use the command database file specified rather than
                        the default.
  -g, --no-global-database
                        Don't load the global system database.
  -l, --list            Print all commands in the database
  -m, --no-commands     Don't show commands in interactive view.
  -n, --no-echo         Don't echo the command to the terminal prior to
                        execution.
  -p PADDING, --label-padding PADDING
                        Add extra padding between labels and commands.
  -s, --search-all      Search both labels and commands. Default is to search
                        only labels first, and only search in commands if
                        searching for labels resulted in no search results.
  -t, --no-labels       Don't display command labels.
  -v, --version         Display program version.

```
# Configuration

In addition to the command line switches a configuration file can be used. The file named `.xxcmdrc` in the current users home directory is loaded if present.

Some options are only configurable through the config file.

An example file demonstrating all possible options (and the system defaults):

```text
[xxcmd]
echo-commands = yes
show-labels = yes
show-commands = yes
align-commands = yes
draw-window-border = yes
label-padding = 2
bracket-labels = no
bold-labels = yes
whole-line-selection = yes
search-labels-only = no
search-labels-first = yes
shell = default
sort-by-label = yes
sort-by-command = no
sort-case-sensitive = yes
display-help-footer = yes
load-global-database = yes
```

Command line switches take precedence over configuration file options.

`shell` can be set to the full path of the shell to be used to execute commands, such as `/bin/sh`. If set to `default` the environmental variable `SHELL` is inspected to use the default OS shell.