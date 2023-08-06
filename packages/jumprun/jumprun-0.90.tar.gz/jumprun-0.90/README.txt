$ _jumprun

A unix command-line tool for running scripts from any directory in
terminal, It allows you to do it from any directory buy making shortcuts. At the current moment Perl 5,
Ruby and Python interpreters are supported.

Platform:
---------
This tool is strictly for UNIX based OS.

Installation:
-------------
It can be installed using PyPi, pip install jumprun.

Dependencies:
-------------
This tool makes use of docopt and termcolor

Usage:
------
Note: The $ (dollar) sign used below only shows that we are in the command-line, it isn't the part of the command

* Add a python shortcut with, $ jr add NAME file.py
* Run the script from any dir in terminal using, $ jr NAME
* Refresh the entire db with, $ jr rm --all
* Delete a specfic shortcut with, $ jr rm NAME
* Rename a shortcut with, $ jr rename OLDNAME NEWNAME
* List all shortcuts with $ jr show
* $ jr --help for more details

Whats new in version 0.8 ?:
----------------------------
You no longer need to specify an interpreter using the --python or --ruby options, now Jumprun will automatically select the interpreter according to the file extension

TODO:
-----
* Add support for shell scripts 

License:
--------
Jumprun is distributed under MIT license, see LICENSE for more details.
