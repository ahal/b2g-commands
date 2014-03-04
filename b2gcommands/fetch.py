#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function

import subprocess
import sys

SVN_NOT_FOUND = '''
Mach could not download mozboot.

Subversion is required to download mozboot. Please
make sure svn is installed. Alternatively you can
run ./config.sh to obtain a copy of the gecko source
tree which contains mozboot.
'''.lstrip()

REPO = 'https://github.com/mozilla/gecko-dev/'

def install_module(module, save_dir='mozboot'):
    print('Attempting to install mozboot...')
    url = REPO + 'trunk/' + module

    command = ['svn', 'export', url, save_dir]
    try:
        subprocess.check_call(command)
    except OSError:
        print(SVN_NOT_FOUND)
        sys.exit(1)

    return save_dir
