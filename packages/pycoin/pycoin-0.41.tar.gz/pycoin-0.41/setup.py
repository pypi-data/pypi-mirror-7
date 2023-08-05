#!/usr/bin/env python

from setuptools import setup

version = "0.41"

setup(
    name="pycoin",
    version=version,
    packages = [
        "pycoin",
        "pycoin.convention",
        "pycoin.ecdsa",
        "pycoin.key",
        "pycoin.tx",
        "pycoin.tx.script",
        "pycoin.serialize",
        "pycoin.services",
        "pycoin.scripts"
    ],
    author="Richard Kiss",
    entry_points = { 'console_scripts':
            [
                'block = pycoin.scripts.block:main',
                'ku = pycoin.scripts.ku:main',
                'tx = pycoin.scripts.tx:main',
                'cache_tx = pycoin.scripts.cache_tx:main',
                'fetch_unspent = pycoin.scripts.fetch_unspent:main',
                ## these scripts are obsolete
                'genwallet = pycoin.scripts.genwallet:main',
                'spend = pycoin.scripts.spend:main',
                'bu = pycoin.scripts.bitcoin_utils:main',
            ]
        },
    author_email="him@richardkiss.com",
    url="https://github.com/richardkiss/pycoin",
    license="http://opensource.org/licenses/MIT",
    description="Utilities for Bitcoin and altcoin addresses and transaction manipulation.",
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],)
