# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import mozdevice
import mozfile
import os

from mach.decorators import (
    CommandProvider,
    Command,
)
from mozbuild.base import (
    MachCommandBase,
    MachCommandConditions as conditions
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

    @Command('clobber', category='build',
        conditions=[conditions.is_b2g],
        description='Clobber the tree (delete the objdir and out directory).')
    def clobber(self):
        self.remove_objdir()
        outdir = os.path.join(self.b2g_home, 'out')
        if os.path.isdir(outdir):
            mozfile.rmtree(outdir)
        return 0

    @Command('build', category='build',
        description='Run the build script.')
    def build_script(self):
        command = os.path.join(self.b2g_home, 'build.sh')

        p = ProcessHandler(command)
        p.run()

        #TODO: Error checking.
        return p.wait()

    @Command('flash', category='build',
        conditions=[conditions.is_b2g],
        description='Flash the current B2G build onto a device.')
    def flash(self):
        command = os.path.join(self.b2g_home, 'flash.sh')
        p = ProcessHandler(command)
        if _is_device_attached():
            p.run()
            return p.wait()
        return 1
