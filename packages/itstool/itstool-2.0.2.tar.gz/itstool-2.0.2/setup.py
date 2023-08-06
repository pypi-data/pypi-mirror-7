#!/usr/bin/env python

# setup.py.in is converted to setup.py by the configure script. This is not
# intended as the recommended way to build and install itstool. See the INSTALL
# file for details on installing with make. This file is here to make it easier
# to upload itstool to pypi.

from distutils.core import setup

setup(name='itstool',
      version='2.0.2',
      description='XML to PO and back again using W3C ITS rules',
      author='Shaun McCance',
      author_email='shaunm@gnome.org',
      url='http://itstool.org/',
      scripts=['itstool'],
      data_files=[('/usr/share/itstool/its', [
          'its/docbook.its',
          'its/docbook5.its',
          'its/its.its',
          'its/mallard.its',
          'its/ttml.its',
          'its/xhtml.its',
      ])]
)
