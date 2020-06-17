#!/usr/bin/env python3

import os
from setuptools import setup

DESCRIPTION = 'A unix shell monad'
PYTHON_REQUIRES = '>=3.6.0'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as fp:
    LONG_DESCRIPTION = fp.read()

setup(
    name = 'unix',
    version = '1.0',
    packages = ['unix'],
    author = 'Jason Wilkes',
    author_email = 'notarealdeveloper@gmail.com',
    url = 'https://github.com/notarealdeveloper/unix',
    python_requires = PYTHON_REQUIRES,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
)
