# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import json
import os

from mach.decorators import (
    CommandProvider,
    Command,
)

here = os.path.abspath(os.path.dirname(__file__))

@CommandProvider
class Info(object):
    """Interface for information related commands."""

    @Command('vendor-ids', category='misc',
        conditions=[lambda x: True],
        description='Prints vendor udev information',)
    def vendors(self):
        with open(os.path.join(here, 'vendors'), 'r') as f:
            print(f.read())
