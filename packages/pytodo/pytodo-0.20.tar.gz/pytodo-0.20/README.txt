$ _pytodo, a simple command line todo application

pytodo - t for short - is a command line todo app for mac and linux. It stores all the tasks in a sqlite database and you can interact with the app using the terminal (see Usage).

Installation:
--------------
pytodo can be installed from pypi using pip install pytodo

Usage:
-------
The $ sign used below shows that we are in the terminal, its not a part of the command.

- Add a task using, $ t add "Buy Bugatti Veryon" (a string is passed in)
- Check as task as done by specifying the id, $ t check 1
- Uncheck a task again by, $ t uncheck 1
- List all pending tasks, $ t ls
- List all tasks, $ t ls --all
- Flush the database, $ t clear
- For more help, $ t --help

License:
---------
pytodo is distributed under MIT license, see LICENSE for more details
