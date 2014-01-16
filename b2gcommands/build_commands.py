# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import conditions
import mozdevice
import mozfile
import os

from mach.decorators import (
    CommandArgument,
    CommandProvider,
    Command,
)
from mozbuild.base import (
    MachCommandBase,
    MachCommandConditions as build_conditions
)
from mozprocess import ProcessHandler

DEVICE_NOT_FOUND = '''
The %s command cannot find a device.

Please make sure your device is connected.
'''.lstrip()

def _is_device_attached(self):
    """Returns True if a device is attached, False if not."""
    try:
        dm = mozdevice.DeviceManagerADB()
        dm.devices()
    except mozdevice.DMError:
        print(DEVICE_NOT_FOUND % 'flash')
        return False
    return True

@CommandProvider
class Build(MachCommandBase):
    """Interface for build related commands."""

    def __init__(self, context):
        MachCommandBase.__init__(self, context)
        self.b2g_home = context.b2g_home
        self.device_name = context.device_name

    @Command('clobber', category='build',
        conditions=[build_conditions.is_b2g],
        description='Clobber the tree (delete the objdir and out directory).')
    def clobber(self):
        self.remove_objdir()
        outdir = os.path.join(self.b2g_home, 'out')
        if os.path.isdir(outdir):
            mozfile.rmtree(outdir)
        return 0

    @Command('build', category='build',
        conditions=[],
        description='Run the build script.')
    @CommandArgument('modules', nargs='*',
                     help='Only build specified sub-modules')
    @CommandArgument('--debug', action='store_true',
                     help='Enable a debug build')
    @CommandArgument('--profiling', action='store_true',
                     help='Enable SPS profiling')
    @CommandArgument('--noftu', action='store_true',
                     help='Disable first time user experience')
    @CommandArgument('--noopt', action='store_true',
                     help='Disable optimizer')
    @CommandArgument('--valgrind', action='store_true',
                     help='Enable valgrind')
    def build_script(self, modules=None, debug=False, profiling=False,
                     noftu=False, noopt=False, valgrind=False):
        command = [os.path.join(self.b2g_home, 'build.sh')]

        if modules:
            command.extend(modules)

        if debug:
            command.insert(0, 'B2G_DEBUG=1')

        if profiling:
            command.insert(0, 'MOZ_PROFILING=1')

        if noftu:
            command.insert(0, 'NOFTU=1')

        if noopt:
            if profiling:
                print("Can't perform profiling if optimizer is disabled")
                return 1
            command.insert(0, 'B2G_NOOPT=1')

        if valgrind:
            command.insert(0, 'B2G_VALGRIND=1')

        p = ProcessHandler(command)
        p.run()

        #TODO: Error checking.
        return p.wait()

    @Command('flash', category='post-build',
        conditions=[build_conditions.is_b2g,
                    conditions.is_device],
        description='Flash the current B2G build onto a device.')
    def flash(self):
        command = os.path.join(self.b2g_home, 'flash.sh')
        p = ProcessHandler(command)
        if _is_device_attached():
            p.run()
            return p.wait()
        return 1
