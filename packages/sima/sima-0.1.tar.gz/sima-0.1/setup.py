#!/usr/bin/env python
from setuptools import setup
from distutils.extension import Extension
import numpy

import sys
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    m.Extension.__dict__ = m._Extension.__dict__


extensions = [
    Extension(
        'sima._motion',
        include_dirs = [numpy.get_include()],
        sources = ['sima/_motion.c']
    )
]

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
License :: OSI Approved
Programming Language :: Python
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: MacOS

"""
setup(
    name = "sima",
    version = "0.1",
    packages = ['sima', 'sima.misc'],
    #   scripts = [''],
    #
    #   # Project uses reStructuredText, so ensure that the docutils get
    #   # installed or upgraded on the target machine
    install_requires = [
        'numpy>=1.6.2',
        'scipy>=0.13.0',
        'matplotlib>=1.2.1',
        'scikit-image>=0.9.3',
        'shapely>=1.2.14',
        'mdp>=3.3',
        #'cv2>=2.4.8',
    ],
    #
    #   package_data = {
    #       # If any package contains *.txt or *.rst files, include them:
    #       '': ['*.txt', '*.rst'],
    #       # And include any *.msg files found in the 'hello' package, too:
    #       'hello': ['*.msg'],
    #   },
    #
    #   # metadata for upload to PyPI
    author = "Patrick Kaifosh, Jeffrey Zaremba, Nathan Danielson",
    author_email = "software@losonczylab.org",
    description = "Software for analysis of sequential imaging data",
    license = "GNU GPLv2",
    keywords = "imaging microscopy neuroscience segmentation",
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    ext_modules = extensions,
    setup_requires=['setuptools_cython'],
    url = "http://www.losonczylab.org/sima/",

    platforms = ["Linux", "Mac OS-X", "Windows"],
    #
    #   # could also include long_description, download_url, classifiers, etc.
)
