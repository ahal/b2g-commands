# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

def is_device(cls):
    """Physical device needs to be configured."""
    return not is_emulator(cls)

def is_emulator(cls):
    """Emulator needs to be configured."""
    return cls.device_name in ('emulator', 'emulator-jb')
