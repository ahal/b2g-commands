# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import conditions
import os

from mach.decorators import (
    CommandProvider,
    Command,
)
try:
    from mozbuild.base import (
        MachCommandBase,
        MachCommandConditions as build_conditions
    )
except ImportError:
    # can't use these commands without a config anyway
    from mozbuild_stub import (
        MachCommandBase,
        MachCommandConditions as build_conditions
    )


@CommandProvider
class Run(MachCommandBase):
    """Interface for run related commands."""

    def __init__(self, context):
        MachCommandBase.__init__(self, context)
        self.b2g_home = context.b2g_home
        self.device_name = context.device_name

    @Command('run-emulator', category='post-build',
        conditions=[build_conditions.is_b2g,
                    conditions.is_emulator],
        description='Run the B2G emulator.')
    def emulator(self):
        command = os.path.join(self.b2g_home, 'run-emulator.sh')

        from mozprocess import ProcessHandler
        p = ProcessHandler(command)
        p.run()

        #TODO The emulator requires adb to run, we should check if that is
        #running, catch that error or better yet, start adb.
        return p.wait()

    @Command('run-gdb', category='post-build',
        conditions=[build_conditions.is_b2g],
        description='Run the GNU Debugger.')
    def gdb(self):
        command = os.path.join(self.b2g_home, 'run-gdb.sh')

        from mozprocess import ProcessHandler
        p = ProcessHandler(command)
        p.run()

        #TODO The emulator requires adb to run, we should check if that is
        #running, catch that error or better yet, start adb.
        return p.wait()
