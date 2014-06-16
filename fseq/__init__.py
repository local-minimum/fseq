"""fSeQ is a toolbox for sequence analysis in the frequency domain.

The module is organized around two phases of work: *importing* and *reporting*.
The importing uses a data format detector `SeqFormatDetector`, a `SeqReader`
and several `SeqEncoder`s. 

The `Report`s and `ReportBuilder` use the output of the import phase to produce
the output.

Import
------

Report
------


See also
--------


References
----------

Examples
--------


"""

from fseq.reading.seq_reader import SeqReader

from fseq.reading.seq_encoder import \
    SeqEncoder, SeqEncoderGC, SeqFormatDetector, \
    FormatError, FormatImplementationError, FormatUnknown, \
    SeqFormat, FastaMultiline, FastaSingleline, FastQ

from fseq.reporting.report_builder import ReportBuilderBase, \
    ReportBuilderPositionAverage

