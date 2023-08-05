#!/usr/bin/env python
from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import doctest
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    import yamlpage as mod
except ImportError:
    DOC = ''
else:
    DOC = mod.__doc__.strip()

NAME = 'yamlpage'
VER = '1.0.0'


open('README.md', 'w').write(DOC)
if sys.argv[-1] == 'publish':
    if not doctest.testfile('README.md').failed:
        os.system('python setup.py sdist upload')
        sys.exit(1)
if len(sys.argv) == 1:
    print('Use "./setup.py register" for registration or update package')
    print('Or  "./setup.py publish" for publication new release')
    sys.exit()


setup(
    name=NAME,
    url='https://github.com/imbolc/%s' % NAME,
    version=VER,
    description=DOC.split('===\n', 1)[-1].strip().split('\n\n')[0],
    long_description=DOC.split('\n\n', 1)[-1],

    py_modules=[NAME],

    author='Imbolc',
    author_email='imbolc@imbolc.name',
    license='ISC',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],

    install_requires=['pyyaml'],
)
