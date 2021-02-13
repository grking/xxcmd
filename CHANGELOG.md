# Changelog

## [0.9.0] - 2021-02-13
- Added support for optional system-wide database. (/etc/xxcmd)
- Added additional window decoration.
- Added footer help mentioning keyboard shortcuts.
- Added a couple of default commands if there is no command database.
- Added feature to add new commands from the interactive view.
- Fixed wasted space when not displaying window decoration.
- Fixed auto run when search term has spaces.
- Fixed line edit allowing non-printable characters.

## [0.8.0] - 2021-02-11
- Added feature to edit existing commands with F2 or CTRL+I.
- Added support for arrow keys, home, end, CTRL+arrow in line editor.
- Added config file option to change shell used to execute commands.
- Added sort options for interactive view. Defaults to sort by label.
- Added command line switch to change command database file.
- Added support for editing really long lines (scrolling edit).
- Fixed missing cursor when editing on some terminals.

## [0.7.0] - 2021-02-09
- Changed default search to search only labels, if no matches try searching commands.
- Added option to not show shell commands in the interactive view.
- Added option to search only labels.
- Added option to search both labels and commands simultaneously.

## [0.6.0] - 2021-02-09
- Added bold label display option.
- Added bracketed label display option.
- Added whole line selection highlight option.
- Added option to create a config file automatically.
- Fixed unused blank column on right margin.

## [0.5.0] - 2021-02-08
- Added support for scrolling through long command lists.
- Added visual border around the window.
- Added option to not show the window border.
- Added option to increase padding between labels and commands.
- Added support for a config file in ~/.xxcmdrc

## [0.4.0] - 2021-02-08
- Added option to not echo commands when executed (-n, --no-echo)
- Changed output of --list to a format which can be imported.
- Fixed crash with very small terminal sizes.

## [0.3.2] - 2021-02-07
- Fixed problem with backspace in vscode terminal.
- Fixed error handling when there are problems importing from a URL.
- Fixed crash when shrinking terminal very small.

## [0.3.1] - 2021-02-07
- Fixed older Python 3 version compatability.

## [0.3.0] - 2021-02-07
- Added support for older versions of Python (3.1)
- Added label editing with F1 or CTRL+E

## [0.2.3] - 2021-02-07
- Fixed detection of shell for command execution.

## [0.2.2] - 2021-02-07
- Fixed crash when deleting non-existant items.
- Fixed detection of BACKSPACE key in some environments.

## [0.2.1] - 2021-02-07

- Removed dependency on Python 3.9 features.
- Added Changelog.

## [0.2.0] - 2021-02-07

- Initial release.