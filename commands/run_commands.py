# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

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

@CommandProvider
class Run(MachCommandBase):
    """Interface for run related commands."""

    def __init__(self, context):
        MachCommandBase.__init__(self, context)
        self.b2g_home = context.b2g_home

    @Command('run-emulator', category='testing',
        conditions=[conditions.is_b2g],
        description='Run the B2G emulator.')
    def emulator(self):
        command = os.path.join(self.b2g_home, 'run-emulator.sh')

        p = ProcessHandler(command)
        p.run()

        #TODO The emulator requires adb to run, we should check if that is
        #running, catch that error or better yet, start adb.
        return p.wait()
