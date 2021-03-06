import warnings
import time
import re

from inspect import getmro

import fseq


def inheritDocFromSeqFormat(f):
    """This decorator will copy the docstring from ``SeqFormat`` for the
    matching function ``f`` if such exists and no docstring has been added
    manually.
    """
    if f.__doc__ is None:

        fname = f.__name__

        for c in getmro(SeqFormat):
            if hasattr(c, fname):
                d = getattr(c, fname).__doc__
                if d is not None:
                    f.__doc__ = d
                    break

    return f


class SeqEncoder(object):
    """Base class for managing encoding of raw input data.

    The encoder coordinates detection of raw data format and then
    extracts the information that the encoder is tasked to extract, 
    convering it into suitable encoding.

    **Note:** The base class is not intended to be used directly, but
    to be extended.

    Attributes
    ----------

    format
    initiated
    itemSize
    qualityEncoding
    sequenceEncoding
    useQuality
    useSequence

    See also
    --------

    SeqEncoderGC: GC encoder
    """

    def __init__(self, expectedInputFormat=None, useSequence=True,
            useQuality=False, sequenceEncoding=None, qualityEncoding=None,
            requestReports=tuple()):
        """
        Paramters
        ---------

        expectedInputFormat: SeqFormatDetector or SeqFormat, optional
            A sequence format expected in the input.
            (Default: Letting encoder guess format from input)

        useSequence: bool
            If encoder will be using the sequence information

        useQuality: bool
            If encoder will be using the quality information

        sequenceEncoding: dict or object implementing ``__getitem__``
            Translation map from input to output

        qualityEncoding: dict or object implementing ``__getitem__``
            Translation map from input to output
        """

        self._qualityEncoding = None
        self._sequenceEncoding = None

        self.reset()

        self.useSequence = useSequence
        self.useQuality = useQuality
        self.requestReports = requestReports

        if expectedInputFormat:
            self.format = expectedInputFormat

        if sequenceEncoding is not None:
            self.sequenceEncoding = sequenceEncoding
        if qualityEncoding is not None:
            self.qualityEncoding = qualityEncoding

    @property
    def format(self):
        """The input format currently expected.

        Returns
        -------

        SeqFormatDetector

        Raises
        ------

        TypeError
            If attempting to set format with object not derived from
            ``SeqFormatDetector`` or ``SeqFormat``
        """

        return self._format

    @format.setter
    def format(self, val):

        if isinstance(val, SeqFormat):
            val = SeqFormatDetector(forceFormat=val)

        if not isinstance(val, SeqFormatDetector):

            raise TypeError("Format {0} is not a ``SeqFormatDetector``".format(
                val))

        else:

            self._format = val

            if not val.detecting:

                if not val.compatible(self):

                    raise FormatError(
                        "Encoder requires information not present in format")


                self._sequenceLine = val.sequenceLine
                self._qualityLine = val.qualityLine
                self._headerLine = val.headerLine

                enc = val.qualityEncoding
                if enc is not None:

                    if self._qualityEncoding is None:

                        self._qualityEncoding = enc

                    else:

                        warnings.warn(
                            "{0} will keep its quality encoding {1}".format(
                                self, self.qualityEncoding) +
                            " and not use {2} from {3}".format(
                                enc, val))

                self._formatCompatible = True

            else:

                self._sequenceLine = None
                self._qualityLine = None 
                self._headerLine = None 

    @property
    def requestReports(self):
        """The reports that the encoder likes to be produced by the reader"""
        return self._requestReports

    @requestReports.setter
    def requestReports(self, rps):

        try:
            rps = tuple(rps)
        except TypeError:
            rps = (rps, )

        self._requestReports = rps

    @property
    def initiated(self):
        """If the sequence encoder is ready to start parsing: bool"""

        return self._format is not None and self._formatCompatible

    @property
    def itemSize(self):
        """The size in number of lines for each item in the source.

        Returns
        -------

        int

        Raises
        ------

        fseq.FormatError
            If encoder is not fully initiated

        See also
        --------

        SeqEncoder.initiated
            The initiation status
        SeqEncoder.detectFormat()
            Detecting the format
        SeqEncoder.format
            Manually setting the format
        """
        if not self.initiated:
            if self._format is None:
                raise FormatError("Encoder has not been formatted")
            else:
                raise FormatError("Encoder and format are incompatible")

        return self._format.itemSize


    @property
    def qualityEncoding(self):
        """Map for translating quality chars to numeric values.

        Returns
        -------

        Object with key-lookup (implementing ``__getitem__``)

        Raises
        ------

        TypeError
            If attempting to set with object not having char key-lookup
        """
        return self._qualityEncoding

    @qualityEncoding.setter
    def qualityEncoding(self, val):

        if not hasattr(val, "__getitem__") and val is not None:

            raise TypeError(
                "{0} does not implement item look-up".format(val))

        else:

            try:
                val['A']
            except TypeError:

                raise TypeError("{0} must be able to take chars as keys".format(
                    val))
            except KeyError:
                self._qualityEncoding = val
            else:
                self._qualityEncoding = val

    @property
    def sequenceEncoding(self):
        """Map for translating sequence chars to numeric values.

        Returns
        -------

        Object with key-lookup (implementing ``__getitem__``)

        Raises
        ------

        TypeError
            If attempting to set with object not having char key-lookup
        """
        return self._sequenceEncoding

    @sequenceEncoding.setter
    def sequenceEncoding(self, val):

        if not hasattr(val, "__getitem__") and val is not None:

            raise TypeError(
                "{0} does not implement item look-up".format(val))

        else:

            try:
                val['A']
            except TypeError:

                raise TypeError("{0} must be able to take chars as keys".format(
                    val))
            except KeyError:
                self._sequenceEncoding = val
            else:
                self._sequenceEncoding = val

    @property
    def useQuality(self):
        """If quality-line is to be used by the encoder.

        Returns
        -------

        bool
        """
        return self._useQuality
    
    @useQuality.setter
    def useQuality(self, val):

        self._useQuality = bool(val)

    @property
    def useSequence(self):
        """If sequence-line is to be used by the encoder

        Returns
        -------

        bool
        """

        return self._useSequence

    @useSequence.setter
    def useSequence(self, val):

        self._useSequence = val

    def feedDetection(self, line):
        """Give detection a line to work with.

        Parameters
        ----------

        line: str
            A line from the source file

        Returns
        -------

        fseq.SeqEncoder
            Returns ``self``
        """

        self._detectFeed.append(line)
        return self

    def detectFormat(self):
        """Detect format based on current input stream

        Returns
        -------

        fseq.SeqEncoder
            Returns ``self``

        Raises
        ------

        FormatError
            If data is not compatible with information requested

        See also
        --------

        SeqEncoder.detectFormat()
            Guessing
        """
        
        if self.initiated:
            return self

        f = SeqFormatDetector()

        while f.detecting:

            if len(self._detectFeed):
                f.feed(self._detectFeed.pop(0))
                if not f.detecting:

                    self._sequenceLine = f.sequenceLine
                    self._qualityLine = f.qualityLine
                    self._headerLine = f.headerLine

                    break

            time.sleep(0.05)

        enc = f.qualityEncoding

        if self.qualityEncoding:

            warnings.warn(
                "{0} got its quality encoding {1}".format(
                    self, self.qualityEncoding) +
                " replaced by {2} to {3}".format(
                    f, enc))

        #Setting to None is just to suppress warning when assigning
        #format.
        self._qualityEncoding = None

        self.format = f


        return self

    def reset(self):
        """Clears the sequence format

        Returns
        -------

        fseq.SeqEncoder
            Returns ``self``

        See also
        --------

        SeqEncoder.detectFormat()
            Guessing
        """

        self._sequenceLine = None
        self._qualityLine = None
        self._headerLine = None

        self._formatCompatible = False
        self._format = None
        self._detectFeed = []

        return self

    def parse(self, lines, out, outindex):
        """Placeholder parser overwritten when subclassing

        Parameters
        ----------

        lines: iterable of str
            Iterable of length equal to ``self.itemSize`` containing the
            raw data for one item

        out: numpy.ndarray
            Array that will have values written to it

        outIndex: object
            Index for where the parse output should be written in the ``out``
            array such that ``out[outIndex]`` gives a sufficiently large array
            that the result of parsing will fit in it.

        Raises
        ------

        NotImplemented
            If base class parse not overwritten or base class used directly
        """

        raise NotImplementedError("``SeqEncoder.parse`` should be overwritten")


class SeqEncoderGC(SeqEncoder):
    """GC Encoder, but useful for any sequence to numerical value encoding.

    The encoder uses the sequence information of the raw data and encodes
    the data according to the following:

    +-------+----------+
    | Input | Encoding |
    +=======+==========+
    | G C   | 1.0      |
    +-------+----------+
    | A T   | 0.0      |
    +-------+----------+
    | N     | 0.5      |
    +-------+----------+

    To change this behaviour, simply submit a new mappable object such as
    e.g. a ``dict`` as the ``sequenceEncoding``-parameter.
    """

    def __init__(self, expectedInputFormat=None, sequenceEncoding=None):
        """
        Parameters
        ----------

        expectedInputFormat: SeqFormatDetector or SeqFormat, optional
            A sequence format expected in the input.
            (Default: Letting encoder guess format from input)
    
        sequenceEncoding: dict or object implementing __getitem__, optional
            (Default: Any G or C value 1; A and T get 0;
            Unknown values such as N get 0.5)
        """
        if sequenceEncoding is None:
            sequenceEncoding = {'G': 1.0, 'C': 1.0, 'A': 0, 'T': 0, ' ': 0.5,
                    'N': 0.5}

        super(SeqEncoderGC, self).__init__(
            expectedInputFormat=expectedInputFormat, useSequence=True,
            useQuality=False, sequenceEncoding=sequenceEncoding,
            qualityEncoding=None,
            requestReports=(fseq.ReportBuilderFFT,
                            fseq.ReportBuilderPositionAverage))

    def parse(self, lines, out, outindex):
        """Encoder of suitable aspects of ``lines`` into ``out``.

        The sequence line of ``lines`` will be encoded onto the index
        ``outindex`` of ``out``.
        If the sequence line is shorter than the data structure of
        ``out[outindex]``, the remainder of ``out[outindex]`` will be left
        untouched.
        If the line is longer, it will only encode up until the the length
        of ``out[outindex]``.

        Parameters
        ----------

        lines: iterable of str
            Iterable of length equal to ``self.itemSize`` containing the
            raw data for one item

        out: numpy.ndarray
            Array that will have values written to it

        outIndex: object
            Index for where the parse output should be written in the ``out``
            array such that ``out[outIndex]`` gives a sufficiently large array
            that the result of parsing will fit in it.
        """

        e = self.sequenceEncoding

        d = [e[char] for char in lines[self._sequenceLine]]

        out[outindex][:len(d)] = d[:out.shape[1]]

#####################################################################
#
# FORMATTERS
#
#
#####################################################################

class FormatError(Exception):
    """Sequence Format Error for exceptions relating to missmatches between
    encoders and sequence formats as well as lacking formattings in encoders
    and unknown sequence formats.
    """

    pass


class FormatImplementationError(FormatError):
    """Error for exposing parts of interface that needs to be overwritten
    in subclasses"""

    pass


class FormatUnknown(FormatError):
    """Error for having no available detectors left"""
    pass


class SeqFormat(object):
    """Base Class for implementing data format detectors.

    The attributes present in subclass should overwrite the
    parent properties. All subclasses must also overwrite the
    ``SeqFormat.expects(line)``.

    Attributes
    ----------

    name
    itemSize
    hasSequence
    hasQuality
    qualityEncoding
    MATCH_AA
    MATCH_AA_S
    MATCH_NT
    MATCH_NT_S
    HEADER_LINE
    SEUENCE_LINE
    QUALITY_LINE

    """

    MATCH_NT = re.compile(r'^[ATCGN]+$', re.IGNORECASE)
    """Matches any complete line of only A T C G or N"""

    MATCH_AA = re.compile(r'^[A-Z]+[*]?$', re.IGNORECASE)
    """Matches any complete line of A-Z characters allowing for asterisc at
    end."""

    MATCH_NT_S = re.compile(r'^[ATCG ]+$', re.IGNORECASE)
    """Matches as ``MATCH_NT`` but extends to include space"""

    MATCH_AA_S = re.compile(r'^[A-Z ]+[*]?$', re.IGNORECASE)
    """Matches as ``MATCH_AA_S`` but extends to include space"""

    HEADER_LINE = 0
    SEQUENCE_LINE = None
    QUALITY_LINE = None

    def __init__(self):

        self._giveup = 20

    @property
    def name(self):
        """Human readable description of format: str"""
        return None

    @property
    def itemSize(self):
        """The size (lines) of each entry: int"""
        return None

    @property
    def hasSequence(self):
        """If format has sequence information: bool"""
        return None

    @property
    def hasQuality(self):
        """If format quality information: bool"""
        return None

    @property
    def qualityEncoding(self):
        """If format comes with a known encoding of quality.

        See also
        --------

        SeqEncoder.qualityEncoding
            Setter of encoder quality.
        """
        return None

    def _decay(self):

        self._giveup -= 1
        return self

    @property
    def givenUp(self):
        """Reports if format has given up even though everything still was
        matching.
        
        The purpose is to be able to promote more restricted formats that
        represents a subset of the more general
        
        Returns
        -------
        
        bool
            The status
        """

        return self._giveup < 0

    def expects(self, line):
        """Test for if line fits into required pattern for the format

        Parameters
        ----------

        line: str
            A line as read from file

        Returns
        -------

        bool

        Raises
        ------
        
        FormatImplementationError
            If ``SeqFormat.expects`` (the base class method) is called.
        """

        raise FormatImplementationError("This method should be overwritten")


class FastaMultiline(SeqFormat):
    """Detector of multi-line FASTA

    **Note:** This format is not supported in the current implementation
        as it has no predictable item-size.

    Attributes
    ----------

    HEADER_LINE
    SEUENCE_LINE
    QUALITY_LINE

    Examples
    --------

    Valid format::

        >Contig_1
        ACAATACA
        GATTACA
        >Contig_2
        ACCCACA
        >Contig_3
        ACCAAACA
        CCAACACA
        ACAACCAC

    See also
    --------

    SeqFormat
        Base class for detectors
    FastaSingleline
        Derived class, with more restricitons
    """

    HEADER_LINE = 0
    SEQUENCE_LINE = -1
    QUALITY_LINE = None

    def __init__(self):

        self._firstLine = True
        self._prevHeader = False
        self._giveup = 20

    def _isHeader(self, line):

        return line.startswith(">")
    
    @property
    @inheritDocFromSeqFormat
    def hasSequence(self):

        return True

    @property
    @inheritDocFromSeqFormat
    def hasQuality(self):

        return False

    @property
    @inheritDocFromSeqFormat
    def name(self):

        return "FASTA:MULTILINE"

    @inheritDocFromSeqFormat
    def expects(self, line):

        h = self._isHeader(line)

        if self.givenUp:
            return False
        elif self._firstLine:
            self._firstLine = False
            self._prevHeader = h
            return h
        else:

            if h:
                if self._prevHeader:
                    return False
                else:
                    self._prevHeader = True
                    self._decay()
                    return True
            elif (re.match(self.MATCH_AA_S, line) or
                    re.match(self.MATCH_NT_S, line)):
                self._prevHeader = False
                return True
            else:
                return False


class FastaSingleline(FastaMultiline):
    """Detector of single-line FASTA format.

    Attributes
    ----------

    HEADER_LINE
    SEUENCE_LINE
    QUALITY_LINE

    Examples
    --------

    Valid format::

        >Contig_1
        AACAATACGA
        >Contig_2
        CCATTTACGA

    See also
    --------

    SeqFormat
        Base class for detectors
    FastaMultiline
        Parent class
    """

    HEADER_LINE = 0
    SEQUENCE_LINE = 1
    QUALITY_LINE = None

    @property
    @inheritDocFromSeqFormat
    def itemSize(self):

        return 2

    @property
    @inheritDocFromSeqFormat
    def name(self):

        return "FASTA:SINGLELINE"

    def _decay(self):

        return self

    @inheritDocFromSeqFormat
    def expects(self, line):

        prevStatus = self._prevHeader
        test = super(FastaSingleline, self).expects(line)
        if not prevStatus and not self._prevHeader:
            return False
        else:
            return test


class FastQ(SeqFormat):
    """Detector of FASTQ format

    **Note:** This class can be subclassed to detect the different
        quality-encoding schemes in the future.

    Attributes
    ----------

    HEADER_LINE
    SEUENCE_LINE
    QUALITY_LINE

    Examples
    --------

    Valid format::

        @Contig_1
        AACAATACGA
        +Contig_1
        @+>AACADGH
        @Contig_2
        CCATTTACGA
        +
        >CCAGJDFGH

    See also
    --------

    SeqFormat
        Base class for detectors
    """

    HEADER_LINE = 0
    SEQUENCE_LINE = 1
    QUALITY_LINE = 3

    def __init__(self):

        super(FastQ, self).__init__()
        self._mod = 0
        self._expectedQlenght = None

                
    def _next(self):

        self._mod = (self._mod + 1) % 4
        
    def _qualExpect(self, line):

        self._decay()
        return self

    @property
    @inheritDocFromSeqFormat
    def name(self):

        return "FASTQ"

    @property
    @inheritDocFromSeqFormat
    def itemSize(self):

        return 4

    @property
    @inheritDocFromSeqFormat
    def hasSequence(self):

        return True

    @property
    @inheritDocFromSeqFormat
    def hasQuality(self):

        return True

    @inheritDocFromSeqFormat
    def expects(self, line):

        ret = False

        if self.givenUp:
            return False
        elif self._mod == 0:
            self._decay()
            ret = line.startswith("@")
        elif self._mod == 1:
            ret = bool(re.match(self.MATCH_AA, line) or
                       re.match(self.MATCH_NT, line))
            self._expectedQlenght = len(line)
        elif self._mod == 2:
            ret = line.startswith("+")
        elif self._mod == 3:
            ret = len(line) == self._expectedQlenght and self._qualExpect(line)
        self._next()
        return ret
    

class SeqFormatDetector(object):
    """Detection of data-format manager

    Given a set of initially specified formats the detector feeds them lines
    of data until only one remains ``True``.
    It then further continues a little while to be more certain that it
    was not a mere fluke.

    Attributes
    ----------

    detecting
    format
    itemSize
    hasSequence
    hasQuality
    qualityEncoding
    headerLine
    sequenceLine
    qualityLine
    headerLine
    sequenceLine
    qualityLine
    FORMATS

    See also
    --------

    SeqFormat: Base class for formats that can be detected.
    """

    FORMATS = [FastaSingleline, FastaMultiline, FastQ]

    def __init__(self, forceFormat=None):
        """
        Parameters
        ----------
        
        forceFormat: SeqFormat, optional
            A format explicitly required. Detection still has to be fed
            lines and succeed.
            
        Raises
        ------

        TypeError
            If ``forceFormat`` is submitted and not a class derived from
            ``SeqFormat``
        """

        self._safetyCheck = None

        self._format = None
        self._itemSize = None
        self._hasSequence = None
        self._hasQuality = None
        self._qualityEncoding = None

        self._qualityLine = None
        self._headerLine = None
        self._sequenceLine = None

        if forceFormat:
            if not isinstance(forceFormat, SeqFormat):
                raise TypeError("{0} not a ``SeqFormat``".format(forceFormat))

            self._possibleFormats = [forceFormat]
            self._setFormat()

        else:
            self._possibleFormats = [f() for f in self.FORMATS]

    @property
    def detecting(self):
        """If attempting to detect: bool"""
        return self._format is None

    @property
    @inheritDocFromSeqFormat
    def itemSize(self):

        return self._itemSize

    @property
    @inheritDocFromSeqFormat
    def hasQuality(self):

        return self._hasQuality

    @property
    @inheritDocFromSeqFormat
    def hasSequence(self):

        return self._hasSequence

    @property
    def format(self):
        """The format name of the detected format: str"""
        return self._format

    @property
    @inheritDocFromSeqFormat
    def qualityEncoding(self):
        
        return self._qualityEncoding

    @property
    def qualityLine(self):
        """The line index in the item for the quality
        
        Returns
        -------
        
        int
        
        Raises
        ------
        
        FormatError
            If attempting to use before format is detected
        """

        if self.detecting:
            raise FormatError("Format is still ambiguious")

        return self._qualityLine

    @property
    def headerLine(self):
        """The line index in the item for the header
        
        Returns
        -------
        
        int
        
        Raises
        ------
        
        FormatError
            If attempting to use before format is detected
        """

        if self.detecting:
            raise FormatError("Format is still ambiguious")

        return self._headerLine

    @property
    def sequenceLine(self):
        """The line index in the item for the sequence
        
        Returns
        -------
        
        int
        
        Raises
        ------
        
        FormatError
            If attempting to use before format is detected
        """

        if self.detecting:
            raise FormatError("Format is still ambiguious")

        return self._sequenceLine

    def _testFormatInformative(self, f):

        if f.itemSize is None:
            raise FormatError(
                "Format {0} detected,".format(f.name) +
                " can't be used due to no fixed item-size")

        if not f.hasSequence and not f.hasQuality:
            raise FormatError(
                "Format {0} detected,".format(f.name) +
                " can't use because has neither sequence nor quality")

        return True

    def compatible(self, encoder):
        """Evaluates if encoder is compatible with the detected format

        Returns
        -------

        bool
            Compatibility

        Raises
        ------

        FormatError
            If attempting to test compatibility before format is detected
        """

        if (self.detecting):
            raise FormatError("Format is still ambiguious")

        return ((not encoder.useSequence or self.hasSequence) and
                (not encoder.useQuality or self.hasQuality))

    def _setFormat(self):

        f = self._possibleFormats[0]
        if self._safetyCheck is None:
            if f.itemSize is None:
                self._safetyCheck = 0
            else:
                self._safetyCheck = f.itemSize
        elif self._safetyCheck > 0:
            self._safetyCheck -= 1

        if self._testFormatInformative(f):
            self._headerLine = f.HEADER_LINE
            self._qualityLine = f.QUALITY_LINE
            self._sequenceLine = f.SEQUENCE_LINE
            self._itemSize = f.itemSize
            self._hasSequence = f.hasSequence
            self._hasQuality = f.hasQuality
            self._qualityEncoding = f.qualityEncoding
            self._format = f.name

    def feed(self, line):
        """Supply a new line to format detector.

        Parameters
        ----------

        line: str
            The next line in the data

        Returns
        -------

        fseq.SeqEncoder
            Returns ``self``

        Raises
        ------

        FormatUnknown
            If no known formatters are left
        """
        self._possibleFormats = [f for f in self._possibleFormats if
                f.expects(line)]
        
        l = len(self._possibleFormats)

        if l == 0:
            raise FormatUnknown(
                    "No known formats left, causing line\n{0}".format(line))
        elif l == 1:

            self._setFormat()

        return self
