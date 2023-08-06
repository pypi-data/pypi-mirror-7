#! /usr/bin/env python
from setuptools import setup
import os

PROJECT_ROOT, _ = os.path.split(__file__)
REVISION = '0.0.5'
PROJECT_NAME = 'blink1'
PROJECT_AUTHORS = "Salim Fadhley"
PROJECT_EMAILS = 'salimfadhley@gmail.com'
PROJECT_URL = "https://bitbucket.org/salimfadhley/blinkone"
SHORT_DESCRIPTION = 'PyUSB-based Blink(1) control library'

try:
    DESCRIPTION = open(os.path.join(PROJECT_ROOT, "readme.rst")).read()
except IOError:
    DESCRIPTION = SHORT_DESCRIPTION

setup(
    name=PROJECT_NAME.lower(),
    version=REVISION,
    author=PROJECT_AUTHORS,
    author_email=PROJECT_EMAILS,
    packages=['blink1', 'blink1_tests'],
    zip_safe=True,
    include_package_data=False,
    install_requires=['pyusb', 'click', 'webcolors'],
    test_suite='nose.collector',
    tests_require=['mock', 'nose', 'coverage'],
    url=PROJECT_URL,
    description=SHORT_DESCRIPTION,
    long_description=DESCRIPTION,
    license='MIT',
    entry_points={
        'console_scripts': [
            'flash = blink1.flash:flash'
        ]
    },
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
    ],
)