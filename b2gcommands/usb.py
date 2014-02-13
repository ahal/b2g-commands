# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import errors
import mozdevice
import subprocess
import sys


def is_attached():
    """Returns True if a device is attached, False if not."""
    try:
        dm = mozdevice.DeviceManagerADB()
        dm.devices()
    except mozdevice.DMError:
        return False
    return True

def _parse_lsusb():
    output = subprocess.check_output(['lsusb', '-v'])
    lines = [l.strip() for l in output.splitlines()]

    devices = []
    data = {}
    for line in lines:
        print(line)
        if line.lower() == 'device descriptor:' and data:
            devices.append(data)
            data = {}
        tokens = line.split()
        if len(tokens) > 0:
            if tokens[0].lower() == 'iserial':
                data['iserial'] = tokens[-1]
            elif tokens[0].lower() == 'idvendor':
                data['idvendor'] = tokens[1]
    if data:
        devices.append(data)
    return devices


def get_vendor_id(serial=None):
    if not serial:
        devices = []
        dm = mozdevice.DeviceManagerADB()
        devices = dm.devices()
        if len(devices) > 1:
            raise errors.MultipleDeviceError
        serial = devices[0][0]

    for device in _parse_lsusb():
        print(device)
        if device['iserial'] == serial:
            return device['idvendor'][2:]
    raise errors.VendorNotFound

def _has_vendor(vendor):
    with open('/etc/udev/rules.d/51-android.rules', 'r') as f:
        lines = f.readlines()
    for line in lines:
        if vendor in line:
            return True
    return False

def _set_vendor(vendor):
    if _has_vendor(vendor):
        return
    line = "SUBSYSTEM=='usb', ATTR{idVendor}=='%s', MODE='0666', GROUP='plugdev'" % vendor
    subprocess.check_call(['sudo', 'echo', '"%s"' % line, '>>', '/etc/udev/rules.d/51-android.rules'])

def create_udev_rules(vendor=None):
    if not vendor:
        vendor = get_vendor_id()

    _set_vendor(vendor)
    _set_vendor('18d1') # some phones also need Google's id
        
