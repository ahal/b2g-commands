# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import argparse
import mozfile
import os

from mach.decorators import (
    CommandArgument,
    CommandProvider,
    Command,
)
from mozbuild.base import (
    MachCommandBase,
)
from mozprocess import ProcessHandler


@CommandProvider
class Sync(object):
    """Interface for sync related commands."""

    def __init__(self, context):
        self.b2g_home = context.b2g_home

    @Command('sync', category='devenv',
        allow_all_args=True,
        conditions=[],
        description='Sync repositories.')
    @CommandArgument('args', nargs=argparse.REMAINDER,
        help='Run |mach sync --help| to see full arguments.')
    def sync(self, args):
        command = [os.path.join(self.b2g_home, 'repo'), 'sync']
        command.extend(args)

        env = os.environ.copy()

        p = ProcessHandler(command, env=env)
        p.run()

        return p.wait()

    @Command('config', category='devenv',
        conditions=[],
        description='Configure a device.')
    @CommandArgument('device', action='store', nargs='?', default=None,
        help='Device to configure.')
    @CommandArgument('--branch', action='store',
        help='Branch to configure, defaults to master.')
    def config(self, device=None, branch=None):
        command = [os.path.join(self.b2g_home, 'config.sh')]
        env = os.environ.copy()

        if branch:
            env['BRANCH'] = branch

        if device:
            command.append(device)

        p = ProcessHandler(command, env=env)
        p.run()

        return p.wait()

        
