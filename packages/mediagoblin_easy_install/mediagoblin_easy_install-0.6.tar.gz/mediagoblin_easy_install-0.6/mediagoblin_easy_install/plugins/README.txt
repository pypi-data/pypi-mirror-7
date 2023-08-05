Plugins for Mediagoblin Easy Install
===================================== 
The Easy Install script does accept plugins, however as this is a simple one
shot program, the plugin-ing system is very simple. To make a new plugin,
take a look at how mediagoblin_easy_install.tasks is set up. There is the
primary InstallationTasks class which defines a slew of different tasks as a
method, and then it runs them all in the order defined by its method `run`

The basics
----------
These plugins are simply based off of python inheritance. To make a new plugin,
just create a new directory inside mediagoblin_easy_install/plugins/ and within
that place an empty file named __init__.py and a file named 'app.py'. You can
look at the core 'app.py' to understand what that file does. Lastly it's
important that you make a simple script to run your program (I do it by importing
and running the application inside app.py) and put this script in the root
mediagoblin_easy_install directory.

Adding new tasks
----------------
If you want to add an extra task to installing mediagoblin, say you wanted to
install a plugin, you would need to make your own `tasks.py` file inside of your
new plugin directory. You could then import the InstallationTasks object from
core, and then create a new object that would inherit from it. And then, all you
need to do is create a new method that installs your plugin, and then override
the InstallationTasks' `run` method with one which may have all of its old
methods, but with your new one added afterwards.
