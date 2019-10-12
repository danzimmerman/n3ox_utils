#-*- coding: utf-8 -*-
import os
from setuptools import setup

def read_desc(fname):
    '''
    Load long description from specified file.
    '''
    this_dir = os.path.abspath(os.path.dirname(__file__))
    descfile = os.path.join(this_dir, fname)
    with open(descfile, encoding='utf-8') as dsf:
        long_desc = dsf.read()

    return long_desc

setup(
    name = 'n3ox-utils',
    version = '0.2.4',
    author = 'Daniel S. Zimmerman, N3OX',
    author_email = 'n3ox@n3ox.net',
    description = ('Antenna and transmission line '
                   'utilities. Near field animations.'),
    license = 'MIT',
    packages = [
                'n3ox_utils',
               ],
    install_requires = [
                        'numpy',
                        'matplotlib',
                        'cycler',
                        'colorcet',
                       ],
    long_description = read_desc('README.md'),

)