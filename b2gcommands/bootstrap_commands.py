# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function, unicode_literals

import conditions
import glob
import os
import platform
import subprocess
import sys
import urllib2
import urlparse

from mach.decorators import (
    CommandProvider,
    Command,
)

here = os.path.abspath(os.path.dirname(__file__))

FINISHED = '''
Your system should be ready to build B2G! If you have not already,
obtain a copy of the source code by running:

    ./mach config <device name>

For a list of possible devices to build against, run:

    ./mach config
'''

PLATFORM_NOT_IMPLEMENTED = '''
It looks like the platform you are using has not been implemented
yet for B2G. We went ahead and installed the Firefox build
pre-requisites for you, but there may be additional steps needed
to build B2G.
'''

SEE_MDN_DOCS = '''
If you encounter build errors see the official documentation
for potential known problems or to install packages manually:

    https://developer.mozilla.org/Firefox_OS/Firefox_OS_build_prerequisites
'''

ARCHITECTURE_NOT_SUPPORTED = '''
A 64 bit operating system is required to build B2G on Linux or Bsd. Sorry :(

See the official documentation for more details:
    https://developer.mozilla.org/Firefox_OS/Firefox_OS_build_prerequisites
'''

OS_NOT_SUPPORTED = '''
It looks like your operating system is not yet supported for B2G. Sorry :(

See the official documentation for more details:
    https://developer.mozilla.org/Firefox_OS/Firefox_OS_build_prerequisites
'''

GCC_USERCONFIG_PROMPT = '''
Your operating system ships with a version of gcc newer than 4.6. We went
ahead and installed gcc-4.6 for you, but we still need to make sure it gets
used for building B2G.

Would you like us to update your .userconfig to do this? [y/N] '''

FEDORA_18_GCC_4_6 = 'http://people.mozilla.org/~gsvelto/gcc-4.6.4-fc18.tar.xz'
FEDORA_19_GCC_4_6 = 'http://people.mozilla.org/~gsvelto/gcc-4.6.4-fc19.tar.xz'

class version(str):
    """subclass for version strings"""
    def __cmp__(self, other):
        if not isinstance(other, basestring):
            raise TypeError
        return cmp(version.normalize(self), version.normalize(other))

    def __eq__(self, other):
        return self.__cmp__(other) == 0
    def __lt__(self, other):
        return self.__cmp__(other) == -1
    def __gt__(self, other):
        return self.__cmp__(other) == 1

    @staticmethod
    def normalize(v):
        parts = [int(x) for x in v.split('.')]
        while parts[-1] == 0:
            parts.pop()
        return parts


class B2GBootstrapper(object):
    def __init__(self, b2g_home):
        self.b2g_home = b2g_home
        self.mozboot_dir = None

        # don't subclass Bootstrapper to avoid global imports
        try:
            from mozboot.bootstrap import Bootstrapper
        except ImportError:
            from fetch import install_module
            self.mozboot_dir = install_module('python/mozboot/mozboot')
            from mozboot.bootstrap import Bootstrapper

        self.boot = Bootstrapper(finished=FINISHED+SEE_MDN_DOCS)
        self.extra_packages = []

    def bootstrap(self):
        try:
            name = self.boot.instance.__class__.__name__
            name = name[:name.index('Bootstrapper')].lower()

            if hasattr(self, 'pre_bootstrap_%s' % name):
                getattr(self, 'pre_bootstrap_%s' % name)()
            else:
                self.boot.finished = PLATFORM_NOT_IMPLEMENTED + SEE_MDN_DOCS
            self.boot.instance.packages.extend(self.extra_packages)

            if name == 'osx':
                # for osx, use the shell script provided in the documentation
                self.boot.instance.ensure_xcode()
                self._download('https://raw.github.com/mozilla-b2g/B2G/master/scripts/bootstrap-mac.sh')
                print('Running the mac bootstrap script...')
                ret = subprocess.call(['bash', 'bootstrap-mac.sh'])
                os.remove('bootstrap-mac.sh')
                print(self.boot.finished)
                return ret

            self.boot.bootstrap()

            if hasattr(self, 'post_bootstrap_%s' % name):
                getattr(self, 'post_bootstrap_%s' % name)()
        finally:
            if self.mozboot_dir:
                import mozfile
                mozfile.remove(self.mozboot_dir)

    def pre_bootstrap_centos(self):
        # XXX please test me
        self.pre_bootstrap_fedora()

    def pre_bootstrap_debian(self):
        self.extra_packages.extend([
            'bison',
            'bzip2',
            'curl',
            'flex',
            'gawk',
            'g++-multilib',
            'git',
            'libgl1-mesa-dev',
            'libx11-dev',
            # 32 bit libraries required to build ics emulator, bug 897727
            'ia32-libs',
            'lib32ncurses5-dev',
            'lib32z1-dev',
        ])


    def pre_bootstrap_fedora(self):
        self.extra_packages.extend([
            'bison',
            'ccache',
            'curl',
            'flex',
            'gawk',
            'libX11-devel',
            'make',
            'patch',
            'zip',
            'perl-Digest-SHA',
            'wget',
            # 32 bit libraries required to build ics emulator, bug 897727
            'ncurses-devel.i686',
            'readline-devel.i686',
            'zlib-devel.i686',
            'libX11-devel.i686',
            'mesa-libGL-devel.i686',
            'glibc-devel.i686',
            'libstdc++.i686',
            'libXrandr.i686',
        ])

    def pre_bootstrap_osx(self):
        """Just use shell script provided in b2g build documentation."""

    def pre_bootstrap_ubuntu(self):
        dist = platform.linux_distribution()[:2]
        dist = (dist[0].lower(), version(dist[1]))

        # we require at least ubuntu 12.04 (linuxmint 13)
        if (dist[0] == 'ubuntu' and dist[1] < '12.04') or \
           (dist[0] == 'linuxmint' and dist[1] < '13') :
            print(OS_NOT_SUPPORTED)
            sys.exit(1)

        if dist in (('ubuntu', '12.04'), ('linuxmint', '13')):
            self.pre_bootstrap_debian()
        elif dist in (('ubuntu', '12.10'), ('linuxmint', '14')):
            # work around error about unmet dependencies for ia32-libs
            self.boot.instance.apt_add_architecture(['i386'])
            self.boot.instance.apt_update()

            self.pre_bootstrap_debian()
            self.extra_packages.extend([
                'gcc-4.6',
                'g++-4.6',
                'g++-4.6-multilib',
            ])
        elif dist in (('ubuntu', '13.04'), ('linuxmint', '15')):
            self.boot.instance.packages.insert(0, '--no-install-recommends')
            self.pre_bootstrap_debian()
            self.extra_packages.extend([
                'gcc-4.6',
                'g++-4.6',
                'g++-4.6-multilib',
            ])
        elif dist in (('ubuntu', '13.10'), ('linuxmint', '16')):
            self.boot.instance.packages.insert(0, '--no-install-recommends')

            # starting in 13.10, multi-arch packages are used
            self.boot.instance.apt_add_architecture(['i386'])
            self.boot.instance.apt_update()

            self.pre_bootstrap_debian()
            self.extra_packages.remove('ia32-libs')
            self.extra_packages.extend([
                'gcc-4.6',
                'g++-4.6',
                'g++-4.6-multilib',
                'zlib1g:amd64',
                'zlib1g-dev:amd64',
                'zlib1g:i386',
                'zlib1g-dev:i386',
                'libxml2-utils',
            ])

    def _append_to_userconfig(self, lines, prompt):
        userconfig = os.path.join(self.b2g_home, '.userconfig')

        lines = ['%s\n' % line for line in lines]
        lines_to_write = []
        if not os.path.isfile(userconfig):
            mode = 'w'
            lines_to_write = lines
        else:
            mode = 'a'
            with open(userconfig, 'r') as f:
                old_lines = f.readlines()
                for line in lines:
                    if line not in old_lines:
                        lines_to_write.append(line)

        if lines_to_write:
            c = raw_input(prompt).lower()
            while c not in ('y', 'n'):
                c = raw_input(prompt).lower()

            if c == 'y':
                with open(userconfig, mode) as f:
                    f.writelines(lines)
            else:
                print('Ok.. but make sure to remember to do it yourself!')

    def _download(self, url, savepath=''):
        print('Downloading %s...' % url)
        try:
            data = urllib2.urlopen(url)
        except urllib2.URLError:
            print('There was a problem downloading the file. Make sure you' \
                  'are connected to the network and try again.')
            sys.exit(1)
        if savepath == '' or os.path.isdir(savepath):
            parsed = urlparse.urlsplit(url)
            filename = parsed.path[parsed.path.rfind('/')+1:]
            savepath = os.path.join(savepath, filename)
        savedir = os.path.dirname(savepath)
        if savedir != '' and not os.path.exists(savedir):
            os.makedirs(savedir)
        outfile = open(savepath, 'wb')
        outfile.write(data.read())
        outfile.close()
        return os.path.realpath(savepath)

    def post_bootstrap_fedora(self):
        cc = None
        cxx = None
        try:
            import which
            try:
                cc = which.which('gcc-4.6')
                cxx = which.which('g++-4.6')
            except which.WhichError:
                pass
        except ImportError:
            pass

        if not cc or not cxx:
            path_names = glob.glob('/opt/gcc-4.6.[0-9]*/bin')
            if not path_names:
                print('gcc-4.6 not detected!')
                v = version(platform.linux_distribution()[1])
                if v in ('17', '18'):
                    path = self._download(FEDORA_18_GCC_4_6)
                    self.boot.instance.run_as_root(['tar', '-xa', '-C', '/opt', '-f', path])
                    os.remove(path)
                elif v in ('19', '20'):
                    path = self._download(FEDORA_19_GCC_4_6)
                    self.boot.instance.run_as_root(['tar', '-xa', '-C', '/opt', '-f', path])
                    os.remove(path)
                else:
                    print("Couldn't find a copy of gcc-4.6 for your platform. You'll need to download and set it up manually.")
                    return
                path_names = glob.glob('/opt/gcc-4.6.[0-9]*/bin')

            # get most recent version
            def sort_path_names(x):
                x = x.split('/')[2]
                return int(x[x.rfind('.')+1:])
            path = sorted(path_names, key=sort_path_names, reverse=True)[0]
            cc = os.path.join(path, 'gcc')
            cxx = os.path.join(path, 'g++')

        write_lines = [
            'export CC=%s' % cc,
            'export CXX=%s' % cxx,
        ]
        self._append_to_userconfig(write_lines, GCC_USERCONFIG_PROMPT)

    def post_bootstrap_ubuntu(self):
        dist = platform.linux_distribution()[:2]
        dist = (dist[0].lower(), version(dist[1]))

        if (dist[0] == 'ubuntu' and dist[1] > '12.04') or \
           (dist[0] == 'linuxmint' and dist[1] > '13'):
            write_lines = [
                'export CC=gcc-4.6',
                'export CXX=g++-4.6',
            ]
            self._append_to_userconfig(write_lines, GCC_USERCONFIG_PROMPT)



@CommandProvider
class Bootstrap(object):
    """Bootstrap system and mach for optimal development experience."""

    def __init__(self, context):
        self.b2g_home = context.b2g_home

    @Command('bootstrap', category='devenv',
        conditions=[lambda x: True],
        description='Install required system packages for building.')
    def bootstrap(self):
        import mozinfo
        if mozinfo.isWin or mozinfo.isBsd:
            print(OS_NOT_SUPPORTED)
            return 1

        if mozinfo.isLinux and mozinfo.bits == 32:
            print(ARCHITECTURE_NOT_SUPPORTED)
            return 1

        bootstrapper = B2GBootstrapper(self.b2g_home)
        bootstrapper.bootstrap()
