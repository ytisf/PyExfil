#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Yuval tisf Nativ'
__license__ = 'GPLv3'
__copyright__ = '2019, Yuval tisf Nativ'

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


required = ['requests>=1.0.0', 'impacket>=0.9.0', 'slackclient', 'progressbar', 'zlib', 'numpy', 'PIL', 'pytube', 'hashlib',
            'urllib2', 'PyCrypto', 'ftplib', 'base58']
            # Todo: Set that urllib2 is not installed from pip for Python3


if __name__ == '__main__':
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    long_desc = open('README.md').read() + '\n\n' + open('LICENSE.md').read()

    setup(name='PyExfil',
        maintainer=__author__,
        maintainer_email='yuval@morirt.com',
        description="""PyExfil: Python communication library over non-standard channels.""",
        license=__license__,
        url='https://www.github.com/ytisf/pyexfil',
        version="1.3",
        download_url='https://www.github.com/ytisf/pyexfil',
        long_description=long_desc,
        packages=['pyexfil'],
        install_requires=required,
        platforms='any',
        classifiers=(
                'Development Status :: 3 - Beta',
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
                'Programming Language :: Python :: 3.5',)
        )
