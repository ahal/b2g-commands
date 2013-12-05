# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

here = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, here)

def list_providers():
    return [os.path.join(here, p) for p in os.listdir(here)
            if os.path.isfile(os.path.join(here, p)) if p.endswith('commands.py')]
