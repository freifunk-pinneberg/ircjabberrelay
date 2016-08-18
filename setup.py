#!/usr/bin/env python

# Copyright (c) 2003-2009 Ralph Meijer
# See LICENSE for details.

from setuptools import setup

setup(name='ircjabberrelay',
      version='0.0.2',
      description='Relay between IRC and Jabber',
      author='Alexey Torkhov | Michel Wohlert',
      author_email='atorkhov@gmail.com',
      maintainer_email='m.wohlert@pinneberg.freifunk.net',
      url='https://github.com/freifunk-pinneberg/ircjabberrelay',
      license='Public Domain',
      platforms='any',
      packages=['ircjabberrelay'],
      data_files=[
            ('/usr/bin', ['ircjabberrelay.tac']),
            ('/etc/ircjabberrelay', ['ignore']),
            ('/etc/init.d',['ircjabberrelay.init'])
      ]
)
