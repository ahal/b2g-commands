b2g-commands
============

A set of mach commands to make working with the B2G repo easier.

Installation
============

Make sure you have pip installed, follow [these instructions](http://www.pip-installer.org/en/latest/installing.html). Then run:


    $ pip install b2g-commands

Upgrade
-------

I may implement an auto-upgrade mechanism in the future. For now, run:
    
    $ pip install --upgrade b2g-commands

Commands
========

You can use b2g-commands to bootstrap your environment, run builds, run config.sh,
run repo sync and much more. For example, after first cloning the B2G repo, you might
do:

    $ ./mach bootstrap        # installs system packages needed to build
    $ ./mach config emulator  # pull in sub-repos needed to build emulator
    $ ./mach build --debug    # build a debug emulator
    $ ./mach run-emulator

For a full list of commands, run:

    $ ./mach help

For information on a specific command, run:

    $ ./mach help <command>
