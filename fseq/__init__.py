#!/usr/bin/env python
"""fSeq is a toolbox for sequence analysis in the frequency domain.

The module is organized around two phases of work: *reading* and *reporting*.

The reading uses a data format detector `SeqFormatDetector`, which detects
the current `SeqFormat` that is being read by the `SeqReader` and passed to the
`SeqEncoder` to translate into a numpy array

The `Report`s and `ReportBuilder` use the output of the import phase to produce
the output. They are organized as such that a builder pre-processes the data
without any graphics done and the reporters the takes the pre-processed data
and make displays out of them.

All relevant parts of *reading* and *reporting* are directly imported to the
package root.

Reading
-------

There is one generic reader that is intended to handle all use cases.

fseq.SeqReader
    Root object that coordinates reading, encoding and reporting

The encoders translates and manages format detection

fseq.SeqEncoder
    Base class encoder
fseq.SeqEncoderGC
    Encoder that translates Gs and Cs to 1 while A and T become 0

There's a general format detector, and several data-formats.

fseq.SeqFormatDetector
    Detector of formats
fseq.SeqFormat
    The base class from which all formats must be derived
fseq.FastaMultiline
    Format detecting a fasta-file where sequence may span more than one line
fseq.FastaSingleline
    Format detecting a fasta-file where sequence is in a signle line
fseq.FastQ
    Format detecting fastq, but not which quality encoding

Reporting
---------

There is a report builder base from which all report builders should be
made, and two specific report builders.

fseq.ReportBuilderBase
    The base class for all builders
fseq.ReportBuilderPositionAverage
    A report builder that averages data per position
fseq.ReportBuilderFFT
    A report builder that subsamples and then does clustered FFT analysis

There are two reports included and an optional base class.

fseq.ReportBase
    Base class to make constructing new reports more efficient
fseq.LinePlot
    Plots a line from the data sent to it
fseq.HeatMap
    Plots a heat-map from the data sent to it.

Exceptions
----------

fseq.FormatError
    Base exception for error with data-formats
fseq.FormatImplementationError
    If a format is not correctly implemented 
fseq.FormatUnknown
    If data is of unknown format
"""

from fseq.reading.seq_reader import SeqReader

from fseq.reading.seq_encoder import \
    SeqEncoder, SeqEncoderGC, SeqFormatDetector, \
    FormatError, FormatImplementationError, FormatUnknown, \
    SeqFormat, FastaMultiline, FastaSingleline, FastQ

from fseq.reporting.reports import ReportBase, LinePlot, HeatMap

from fseq.reporting.report_builder import ReportBuilderBase, \
    ReportBuilderPositionAverage, ReportBuilderFFT
