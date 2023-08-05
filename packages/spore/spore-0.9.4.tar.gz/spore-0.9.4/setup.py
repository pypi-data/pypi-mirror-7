#!/usr/bin/env python

from distutils.core import setup

setup(name='spore',
      version='0.9.4',
      description='Simple P2P Framework',
      author='Kitten Tofu',
      author_email='kitten@eudemonia.io',
      url='http://eudemonia.io/spore/',
      packages=['spore'],
      install_requires=['encodium'],
      #cmdclass={'build_py': build_py, 'clean': clean},
     )
