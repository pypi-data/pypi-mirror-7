# This file is part of the Juju Quickstart Plugin, which lets users set up a
# Juju environment in very few steps (https://launchpad.net/juju-quickstart).
# Copyright (C) 2013 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License version 3, as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Juju Quickstart distribution file."""

import os

from setuptools import (
    find_packages,
    setup,
)


ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_NAME = 'quickstart'

project = __import__(PROJECT_NAME)
description_path = os.path.join(ROOT, 'README.rst')

requirements_path = os.path.join(ROOT, 'requirements.pip')
requirements = [i.strip() for i in open(requirements_path).readlines()]
install_requires = [i for i in requirements if i and not i.startswith('#')]

os.chdir(ROOT)

data_files = []
for dirpath, dirnames, filenames in os.walk(PROJECT_NAME):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'):
            del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(
                dirpath[len(PROJECT_NAME) + 1:], f))


setup(
    name='juju-quickstart',
    version=project.get_version(),
    description=project.__doc__,
    long_description=open(description_path).read(),
    author='The Juju GUI team',
    author_email='juju-gui@lists.ubuntu.com',
    url='https://launchpad.net/juju-quickstart',
    keywords='juju quickstart plugin',
    packages=find_packages(),
    package_data={PROJECT_NAME: data_files},
    scripts=['juju-quickstart'],
    install_requires=install_requires,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup',
    ],
)
