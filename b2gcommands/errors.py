DEVICE_NOT_FOUND = '''
The %s command cannot find a device.

Please make sure your device is connected.
'''.lstrip()

MORE_THAN_ONE_DEVICE = '''
There is more than one device connected via USB.

Please disconnect all devices except the one you
wish to perform the %s command on.
'''.lstrip()

DEVICE_VENDOR_NOT_FOUND = '''
Mach could not detect your device's vendor id.

You need to configure udev rules manually. To do
this, edit /etc/udev/rules.d/51-android.rules and
add a line of the form:

    SUBSYSTEM=="usb", ATTR{idVendor}=="18d1", MODE="0666", GROUP="plugdev"

Replace the idVendor attribute with your device's
vendor id. Run 'mach vendor-ids' to see a list of
common vendor ids.
'''.lstrip()



class MultipleDeviceError(Exception):
    pass

