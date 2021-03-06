# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import conditions
import os
import usb

from mach.decorators import (
    CommandArgument,
    CommandProvider,
    Command,
)
try:
    from mozbuild.base import (
        MachCommandBase,
        MachCommandConditions as build_conditions
    )
except ImportError:
    from mozbuild_stub import (
        MachCommandBase,
        MachCommandConditions as build_conditions
    )


@CommandProvider
class Build(MachCommandBase):
    """Interface for build related commands."""

    def __init__(self, context):
        MachCommandBase.__init__(self, context)
        self.b2g_home = context.b2g_home
        self.device_name = context.device_name

    @Command('clobber', category='build',
        conditions=[conditions.is_configured],
        description='Clobber the tree (delete the objdir and out directory).')
    def clobber(self):
        self.remove_objdir()
        outdir = os.path.join(self.b2g_home, 'out')
        if os.path.isdir(outdir):
            import mozfile
            mozfile.rmtree(outdir)
        return 0

    @Command('build', category='build',
        conditions=[conditions.is_configured],
        description='Run the build script.')
    @CommandArgument('modules', nargs='*',
                     help='Only build specified sub-modules')
    @CommandArgument('-j', action='store', dest='cores',
                     help='Number of cores to use')
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
    def build_script(self, modules=None, cores=None, debug=False,
                     profiling=False, noftu=False, noopt=False, valgrind=False):
        command = [os.path.join(self.b2g_home, 'build.sh')]
        env = os.environ.copy()

        if modules:
            command.extend(modules)

        if cores:
            command.append('-j%s' % cores)

        if debug:
            env['B2G_DEBUG'] = '1'

        if profiling:
            env['MOZ_PROFILING'] = '1'

        if noftu:
            env['NOFTU'] = '1'

        if noopt:
            if profiling:
                print("Can't perform profiling if optimizer is disabled")
                return 1
            env['B2G_NOOPT'] = '1'

        if valgrind:
            env['B2G_VALGRIND'] = '1'

        from mozprocess import ProcessHandler
        p = ProcessHandler(command, env=env)
        p.run()

        #TODO: Error checking.
        return p.wait()

    @Command('flash', category='post-build',
        conditions=[build_conditions.is_b2g,
                    conditions.is_device],
        description='Flash the current B2G build onto a device.')
    @CommandArgument('partitions', nargs='*',
                     help='Only flash specified partitions')
    @CommandArgument('--app', action='store',
                     help='Update only a specific app')
    def flash(self, partitions=None, app=None):
        usb.verify_device('flash')

        command = os.path.join(self.b2g_home, 'flash.sh')
        if partitions:
            command.extend(partitions)

        if app:
            command.insert(0, 'BUILD_APP_NAME=%s' % app)

        from mozprocess import ProcessHandler
        p = ProcessHandler(command)
        p.run()
        return p.wait()
