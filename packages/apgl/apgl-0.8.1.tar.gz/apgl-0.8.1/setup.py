#!/usr/bin/env python
#The first line is needed for egg files and the second for tars etc.
from setuptools import setup
#from distutils.core import setup

#Support for python 3
def execfile3(file, globals=globals(), locals=locals()):
    with open(file, "r") as fh:
        exec(fh.read()+"\n", globals, locals)

execfile3('apgl/version.py')

descriptionFile = open("Description.rst")
description = "".join(descriptionFile.readlines()) 
descriptionFile.close()

setup (
  name = 'apgl',
  version = __version__,
  packages = ['apgl', 'apgl.generator', 'apgl.generator.test', 'apgl.graph', 'apgl.graph.test', 'apgl.io', 'apgl.util', 'apgl.util.test'],
  install_requires=['numpy>=1.5.0', 'scipy>=0.7.1'],
  author = 'Charanpal Dhanjal',
  author_email = 'charanpal@gmail.com',
  url = 'http://packages.python.org/apgl/',
  license = 'GNU Library or Lesser General Public License (LGPL)',
  long_description=description,
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    ],

  keywords=['graph library', 'numpy', 'scipy', 'machine learning'],
  platforms=["OS Independent"],
)
