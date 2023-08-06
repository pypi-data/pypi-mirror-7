#!/usr/bin/env python

from distutils.core import setup
from bibtexparser import __version__ as version

setup(
    name         = 'bibtexparser',
    version      = version,
    url          = "https://github.com/sciunto-org/python-bibtexparser",
    author       = "Francois Boulogne and other contributors",
    license      = "LGPLv3 or BSD",
    author_email = "fboulogne@sciunto.org",
    description  = "Bibtex parser for python 2 and 3",
    packages = ['bibtexparser'],
)
