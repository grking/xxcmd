# xxcmd

![Python Build](https://github.com/grking/xxcmd/workflows/Python%20Build/badge.svg)

`xx` is a Linux shell command. `xx` remembers other shell commands, so you don't have to.

# Installation

Requires Python 3. Installation is simple using `pip`.

On Ubuntu:

```bash
sudo pip3 install xxcmd
```

On Arch:

```bash
sudo pip install xxcmd
```

Or remove `sudo` if you want to install just for the current user and you have pip's local bin on your PATH.

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
* Any other key press is added to the interactive search to filter the command list.

# Further Usage

```text
usage: xx [-h] [-a ...] [-i URL] [-l] [-t] [-v] [cmd]

positional arguments:
  cmd                   Search for a matching command
                        and run it immediately.

optional arguments:
  -h, --help            show this help message and exit
  -a ..., --add ...     Add the given command to the
                        database. Command may begin
                        with a label enclosed in square
                        brackets [label] <cmd>
  -i URL, --import-url URL
                        Import a command database from
                        the given URL. Merge into existing
                        database.
  -l, --list            Print all commands in the database
  -n, --no-echo         Don't echo the command to the terminal
                        prior to execution.
  -t, --no-labels       Don't display command labels.
  -v, --version         Display program version.
```