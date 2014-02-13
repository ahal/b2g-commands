# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import errors
import subprocess
import sys

def verify_device(command):
    """
    Verifies we can connect to the device and errors
    out if not.
    """
    proc = subprocess.Popen(["adb", "devices"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    lines = proc.communicate()[0].splitlines()
    lines = lines[1:]
    lines = [l for l in lines if l.strip() != '']
   
    if not lines:
        print(errors.DEVICE_NOT_FOUND % command)
        sys.exit(1)

    if len(lines) > 1:
        print(errors.MORE_THAN_ONE_DEVICE % command)
        sys.exit(1)

    for line in lines:
        tokens = line.split()
        if tokens[0].startswith('???'):
            print(errors.UDEV_NOT_CONFIGURED % command)
            sys.exit(1)
