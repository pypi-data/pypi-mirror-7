#!/usr/bin/env python
# This file is part of Tryton. The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from setuptools import setup

VERSION = '3.2.0.1'

major_version, minor_version, _ = VERSION.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

requires = []
requires.append(
    'trytond >= %s.%s, < %s.%s' %
    (major_version, minor_version, major_version, minor_version + 1)
)

setup(
    name='openlabs_report_webkit',
    version=VERSION,
    description="Tryton Webkit Report",
    author="Openlabs Technologies & consulting (P) Limited",
    author_email='info@openlabs.co.in',
    url='http://www.openlabs.co.in',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Tryton',
        'Topic :: Office/Business',
    ],
    packages=[
        'openlabs_report_webkit',
    ],
    package_dir={
        'openlabs_report_webkit': 'report',
    },
    license='GPL-3',
    install_requires=requires,
    tests_require=[
        'pyPDF',     # Check if the resultant pdf has the same content
    ],
    zip_safe=False,
    test_suite='tests.suite',
    test_loader='trytond.test_loader:Loader',
)
