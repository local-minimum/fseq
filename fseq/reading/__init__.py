#!/usr/bin/env python
"""Reading-related modules of fseq.

The reading package contains of two modules: `seq_encoder` and `seq_reader`.

The reader contains the generic reader that coordinates actions and works as
the mainframe of `fseq`.
This module should need no extensions to increase the funcitonality of the
`fseq`.

The encoder-module contains both the different types of encoders available as
well as the format-detectors for variaous types of input formats.
Here further formats can be added and new encoders written to extend the 
functionality of `fseq`.
"""
