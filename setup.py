#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Yuval tisf Nativ'
__license__ = 'GPLv3'
__copyright__ = '2020, Yuval tisf Nativ'

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = [
        'requests>=1.0.0', 'impacket>=0.9.0', 'slackclient', 'progressbar',
        'zlib', 'numpy', 'Pillow', 'pytube', 'hashlib', 'urllib2', 'PyCrypto',
        'ftplib', 'base58'
        ]


if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    long_desc = "See full README and USAGE on GITHUB yisf PyExfil."

    setup(name='PyExfil',
        maintainer=__author__,
        maintainer_email='yuval@morirt.com',
        description="A Python package for data exfiltration.",
        license=__license__,
        url='https://pyexfil.morirt.com/',
        version="1.10.4",
        download_url='https://www.github.com/ytisf/pyexfil',
        long_description=long_desc,
        packages=['pyexfil'],
        install_requires=required,
        platforms='any',
        classifiers=(
                'Intended Audience :: Developers',
                'Intended Audience :: Science/Research',
                'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                'Topic :: Software Development',
                'Topic :: Scientific/Engineering',
                'Environment :: Console',
                'Operating System :: Microsoft :: Windows',
                'Operating System :: POSIX',
                'Operating System :: Unix',
                'Operating System :: MacOS',
                'Programming Language :: Python',
                'Programming Language :: Python :: 3',)
        )
