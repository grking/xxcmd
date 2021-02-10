# xxcmd

![](https://img.shields.io/pypi/pyversions/xxcmd) ![](https://img.shields.io/github/workflow/status/grking/xxcmd/Python%20Build) ![](https://img.shields.io/pypi/v/xxcmd) ![](https://img.shields.io/github/commits-since/grking/xxcmd/v0.7.0)

`xx` is a Linux shell command. `xx` remembers other shell commands, so you don't have to.

# Installation

Requires Python 3. Installation is simple using `pip`.

```bash
pip install xxcmd
```

Or `pip3` on Ubuntu or Debian based distros.

If typing `xx` at a command prompt gives you "Command not found", you likely don't have `~/.local/bin` on your PATH. Either install globally with `sudo pip install xxcmd` or add `~/.local/bin` to your PATH.

# Basic Usage Examples

Using `xx` is pretty simple. You build up a database of useful commands, and search and execute them whenever you like.

## Adding Commands

Commands are added to the database with:

`xx -a [label] <command>`

Add a very simple command `top`. Not very useful as the command is already short and easy to remember.

```bash
xx -a top
```

Add the `du` command to display size of all files and directories in the current directory.

```bash
xx -a du --max-depth=1 -h .
```

Add the same command but with a friendly (searchable) label:

```bash
xx -a [File Size] du --max-depth=1 -h .
```

Adding our favourite ssh command:

```bash
xx -a [SSH Best Host] ssh -i ~/.ssh/mykey.pem me@myhost.com
```

## Browse and Search Commands Interactively

Run `xx` with no options to enter the interactive UI.

```bash
xx
```

## Fast search and execute

`xx` can search for matching commands and if only one match is found it will be immediately executed. To run the command we just added we could search for "du":

```bash
xx du
```

Or to run it by searching for a partial match of the label we added:

```bash
xx size
```

We could immediately ssh connect with:

```bash
xx best
```

# Interactive UI

Invoking `xx` without options will open the interactive UI. Presenting a list of all commands with an interactive search.

Keys:

* UP/DOWN arrow keys - navigate the list of commands.
* DELETE - remove the currently selected command
* RETURN - execute the currently selected command
* ESCAPE - exit
* F1 or CTRL+E - Edit the label of the currently selected item
* F2 or CTRL+I - Edit the label of the currently selected item
* Any other key press is added to the interactive search to filter the command list.

# Further Usage

```text
usage: xx [-h] [-a ...] [-i URL] [-c] [-l] [-m] [-n] [-p PADDING] [-s] [-t]
          [-b] [-v]
          [cmd]

A helper for remembering useful shell commands. Type to interactively search,
use UP and DOWN arrows to select, RETURN to launch the selected command. Use
DELETE to remove the currently selected row. F1 or CTRL+E to edit the label of the selected item.

positional arguments:
  cmd                   Search for a matching command and run it immediately.

optional arguments:
  -h, --help            show this help message and exit
  -a ..., --add ...     Add the given command to the database. Command may
                        begin with a label enclosed in square brackets [label]
                        <cmd>
  -i URL, --import-url URL
                        Import a command database from the given URL. Merge
                        into existing database.
  -c, --create-config   Create a config file in the users home directory if
                        one doesn't already exist.
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
  -b, --no-border       Don't display a window border.
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
```

Command line switches take precedence over configuration file options.

`shell` can be set to the full path of the shell to be used to execute commands, such as `/bin/sh`. If set to `default` the environmental variable `SHELL` is inspected to use the default OS shell.