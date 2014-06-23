#!/usr/bin/env python

from distutils.core import setup

setup(
    name='fSequenceTools',
    version='1.0.0',
    description='Sequence numeric encoding and report building tools',
    long_description=\
    '''
==============
fSequenceTools
==============

This package was created to investigate two separate aspects of sequences
analysis:

Encoding time
    By using threading the reading job is split between reading data,
    detecting formats, and encoding sequence data. The structure is fully
    extensible to cover more formats and new types of encoders.

Reporting
    Reports are put together in groups so that secondary analysis of
    encoded data can be shared by a group of different ploting and statistics
    producers.

    ''',
    author='Martin Zackrisson',
    author_email='martin.zackrisson@gu.se',
    url='https://gitorious.org/fseq',
    packages=['fseq', 'fseq.reading', 'fseq.reporting'],
    licence='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)
