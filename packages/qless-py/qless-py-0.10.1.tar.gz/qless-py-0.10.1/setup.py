#! /usr/bin/env python

from distutils.core import setup

setup(
    name                 = 'qless-py',
    version              = '0.10.1',
    description          = 'Redis-based Queue Management',
    long_description     = '''
Redis-based queue management, with heartbeating, job tracking,
stats, notifications, and a whole lot more.''',
    url                  = 'http://github.com/seomoz/qless-py',
    author               = 'Dan Lecocq',
    author_email         = 'dan@seomoz.org',
    license              = "MIT License",
    keywords             = 'redis, qless, job',
    packages             = ['qless', 'qless.workers'],
    package_dir          = {
        'qless': 'qless',
        'qless.workers': 'qless/workers'},
    package_data         = {'qless': ['qless-core/*.lua']},
    include_package_data = True,
    scripts              = ['bin/qless-py-worker'],
    extras_require       = {
        'ps': ['setproctitle']
    },
    install_requires     = [
        'argparse', 'decorator', 'hiredis', 'redis', 'psutil', 'simplejson'],
    classifiers          = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent'
    ]
)
