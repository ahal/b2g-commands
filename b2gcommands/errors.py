# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import mozinfo

DEVICE_NOT_FOUND = '''
The %s command cannot find a device.

Please make sure your device is connected.
'''.lstrip()

MORE_THAN_ONE_DEVICE = '''
There is more than one device connected via USB.

Please disconnect all devices except the one you
wish to perform the %s command on.
'''.lstrip()

UDEV_NOT_CONFIGURED = '''
The %s command cannot connect to the device because
udev rules are not configured.

To do this, edit /etc/udev/rules.d/51-android.rules
and add a line of the form:

    SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"

Replace the idVendor attribute with your device's
vendor id. Run 'mach vendor-ids' to see a list of
common vendor ids.
'''.lstrip()
