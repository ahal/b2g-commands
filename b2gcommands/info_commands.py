# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import json
import os

from mach.decorators import (
    CommandProvider,
    CommandArgument,
    Command,
)

here = os.path.abspath(os.path.dirname(__file__))

@CommandProvider
class Info(object):
    """Interface for information related commands."""

    @Command('vendor-id', category='misc',
        conditions=[lambda x: True],
        description='Prints vendor udev information',)
    @CommandArgument('vendor', action='store', nargs='?',
        help='Return id of specified vendor')
    def vendors(self, vendor=None):
        output = None
        with open(os.path.join(here, 'vendors'), 'r') as f:
            output = f.read()

        if vendor:
            for line in output.splitlines():
                tokens = [t.lower() for t in line.split()]
                if tokens and tokens[0].strip() == vendor.lower():
                    print(tokens[1].strip())
                    return
            print("Vendor '%s' not found!" % vendor)
            return 1
        print(output)
