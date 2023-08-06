#!/usr/bin/env python
import Cython.Distutils
from Cython.Distutils import Extension
import distutils.core
import os
from os import path
from glob import glob


includes = ['murmurhash/']
if 'VIRTUAL_ENV' in os.environ:
    includes += glob(path.join(os.environ['VIRTUAL_ENV'], 'include', 'site', '*'))
else:
    # If you're not using virtualenv, set your include dir here.
    pass

exts = [
    Extension('murmurhash.mrmr', ["murmurhash/mrmr.pyx", "murmurhash/MurmurHash2.cpp",
              "murmurhash/MurmurHash3.cpp"], language="c++", include_dirs=includes),
]


distutils.core.setup(
    name='murmurhash',
    packages=['murmurhash'],
    package_data={'murmurhash': ['*.h', '*.pxd']},
    author='Matthew Honnibal',
    author_email='honnibal@gmail.com',
    version='0.14',
    cmdclass={'build_ext': Cython.Distutils.build_ext},
    ext_modules=exts,
    classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Console',
                'Operating System :: OS Independent',
                'Intended Audience :: Science/Research',
                'Programming Language :: Cython',
                'Topic :: Scientific/Engineering'],
    headers=["murmurhash/MurmurHash2.h", "murmurhash/MurmurHash3.h"]
)
