# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from setuptools import setup, find_packages

PACKAGE_VERSION = '0.10'

deps = []

setup(name='b2g-commands',
      version=PACKAGE_VERSION,
      description='A set of mach commands to make working with the B2G repo easier.',
      long_description='See https://github.com/ahal/b2g-commands',
      classifiers=['Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   ],
      keywords='mozilla',
      author='Andrew Halberstadt',
      author_email='ahalberstadt@mozilla.com',
      url='https://github.com/ahal/b2g-commands',
      license='MPL 2.0',
      packages=['b2gcommands'],
      include_package_data=True,
      zip_safe=False,
      install_requires=deps,
      entry_points="""
        [mach.b2g.providers]
        list_b2g_providers=b2gcommands:list_providers
      """)
