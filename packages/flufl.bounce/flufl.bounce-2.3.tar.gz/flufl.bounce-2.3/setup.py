# Copyright (C) 2004-2014 by Barry A. Warsaw
#
# This file is part of flufl.bounce.
#
# flufl.bounce is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# flufl.bounce is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.bounce.  If not, see <http://www.gnu.org/licenses/>.

import sys

from setup_helpers import (
    description, find_doctests, get_version, long_description, require_python)
from setuptools import setup, find_packages


require_python(0x20600f0)
__version__ = get_version('flufl/bounce/__init__.py')


# Don't try to fix the tests messages.
doctests = [doctest for doctest in find_doctests()
            if 'tests/data' not in doctest]

install_requires = ['zope.interface']
if sys.version_info < (3, 4):
    install_requires.append('enum34')


setup(
    name='flufl.bounce',
    version=__version__,
    namespace_packages=['flufl'],
    packages=find_packages(),
    include_package_data=True,
    maintainer='Barry Warsaw',
    maintainer_email='barry@python.org',
    description=description('README.rst'),
    long_description=long_description('README.rst', 'flufl/bounce/NEWS.rst'),
    license='LGPLv3',
    url='http://launchpad.net/flufl.bounce',
    download_url='https://launchpad.net/flufl.bounce/+download',
    install_requires=install_requires,
    test_suite='flufl.bounce.tests',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: '
            'GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Communications :: Email',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ]
    )
