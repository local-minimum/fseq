import warnings
import time
import re

class SeqEncoder(object):

    def __init__(self, expectedInputFormat=None, useSequence=True,
            useQuality=False, seqenceEncoding=None, qualityEncoding=None):
        """
        Paramters
        ---------

        expectedInputFormat: SeqFormatDetector, optional
            A seqence format expected in the input.
            (Default: Letting encoder guess format from input)

        useSequence: bool
            If encoder will be using the sequence information

        useQuality: bool
            If encoder will be using the quality information

        seqenceEncoding: dict or object implementing __getitem__
            Translation map from input to output

        qualityEncoding: dict or object implementing __getitem__
            Translation map from input to output
        """

        self._qualityEncoding = None
        self._sequenceEncoding = None

        self._formatCompatible = False
        self._format = None
        self._detectFeed = []

        if expectedInputFormat:
            self.format = expectedInputFormat

        self.useSequence = useSequence
        self.useQuality = useQuality

        if seqenceEncoding:
            self.seqenceEncoding = seqenceEncoding
        if qualityEncoding:
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
            `SeqFormatDetector`
        """

        return self._format

    @format.setter
    def format(self, val):

        if not isinstance(val, SeqFormatDetector):

            raise TypeError("Format {0} is not a `SeqFormatDetector`".format(
                val))

        else:

            self._format = val
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
        if not initiated:
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

        Object with key-lookup (implementing __getitem__)
        """
        return self._qualityEncoding

    @qualityEncoding.setter
    def qualityEncoding(self, val):

        if not hasattr(val, "__getitem__") and val is not None:

            raise TypeError(
                "{0} does not implement item look-up".format(val))

        else:

            self._qualityEncoding = val

    @property
    def seqenceEncoding(self):
        """Map for translating sequence chars to numeric values.

        Returns
        -------

        Object with key-lookup (implementing __getitem__)
        """
        return self._sequenceEncoding

    @seqenceEncoding.setter
    def seqenceEncoding(self, val):

        if not hasattr(val, "__getitem__") and val is not None:

            raise TypeError(
                "{0} does not implement item look-up".format(val))

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
            Returns `self`
        """

        self._detectFeed.append(line)
        return self

    def detectFormat(self):
        """Detect format based on current input stream

        Returns
        -------

        fseq.SeqEncoder
            Returns `self`

        See also
        --------

        SeqEncoder.detectFormat()
            Guessing
        """

        f = SeqFormatDetector()

        while f.detecting:

            if len(self._detectFeed):
                f.feed(self._detectFeed.pop(0))
                if not f.detecting:
                    break

            time.sleep(0.05)

        if not f.compatible(self):

            raise FormatError(
                "Encoder requires information not present in format")

        enc = f.qualityEncoding

        if self.qualityEncoding:

            warnings.warn(
                "{0} got its quality encoding {1}".format(
                    self, self.qualityEncoding) +
                " replaced by {2} to {3}".format(
                    f, enc))

        self._qualityEncoding = None
        self.format = f

        return self

    def reset(self):
        """Clears the sequence format

        Returns
        -------

        fseq.SeqEncoder
            Returns `self`

        See also
        --------

        SeqEncoder.detectFormat()
            Guessing
        """
        self._format = None

        return self

    def parse(self, lines, out, outindex):
        """Placeholder parser overwritten when subclassing

        Parameters
        ----------

        lines: iterable of str
            Iterable of length equal to `self.itemSize` containing the
            raw data for one item

        out: numpy.ndarray
            Array that will have values written to it

        outIndex: object
            Index for where the parse output should be written in the `out`
            array such that `out[outIndex]` gives a sufficiently large array
            that the result of parsing will fit in it.
        """

        raise NotImplemented("`SeqEncoder.parse` should be overwritten")


class FormatError(StandardError):
    """Sequence Format Error for exceptions relating to missmatches between
    encoders and sequence formats as well as lacking formattings in encoders
    and unknown sequence formats.
    """
    pass


class SeqFormat(object):

    MATCH_NT = re.compile(r'^[ATCG]+$', re.IGNORECASE)
    MATCH_AA = re.compile(r'^[A-Z]+$', re.IGNORECASE)

    @property
    def name(self):
        return "UNKNOWN"

    @property
    def itemSize(self):

        return None

    @property
    def hasSequence(self):
        return None

    @property
    def hasQuality(self):
        return None

    @property
    def qualityEncoding(self):
        return None

    def expects(self, line):

        raise FormatError("This method should be overwritten")


class FastaMultiline(SeqFormat):

    def __init__(self):

        self._firstLine = True
        self._prevHeader = False
        self._giveup = 20

    def _isHeader(self, line):

        return line.startswith(">")
    
    @property
    def hasSequence(self):

        return True

    @property
    def hasQuality(self):

        return False

    @property
    def name(self):

        return "FASTA:MULTILINE"

    def _decay(self):

        self._giveup -= 1
        return self._giveup > 0

    def expects(self, line):

        h = self._isHeader(line)

        if self._firstLine:
            self._firstLine = False
            self._prevHeader = h
            return h
        else:
            if h:
                if self._prevHeader:
                    return False
                else:
                    self._prevHeader = True
                    if not self._decay():
                        return False
                    return True
            elif re.match(self.MATCH_AA, line) or re.match(self.MATCH_NT, line):
                return True
            else:
                return False


class Fasta(FastaMultiline):

    @property
    def itemSize(self):

        return 2

    @property
    def name(self):

        return "FASTA:SINGLELINE"

    def _decay(self):

        return True

    def expects(self, line):

        prevStatus = self._prevHeader
        test = super(Fasta, self).expects(line)
        if not prevStatus and not self._prevHeader:
            return False
        else:
            return test


class FastQ(SeqFormat):

    def __init__(self):

        self._mod = 0
        self._giveup = 20

                
    def _next(self):

        self._mod = (self._mod + 1) % 4
        
    def _qualExpect(self, line):

        return True

    @property
    def name(self):

        return "FASTQ"

    @property
    def itemSize(self):

        return 4

    @property
    def hasSequence(self):

        return True

    def hasQuality(self):

        return True

    def _decay(self):

        self._giveup -= 1
        return self._giveup > 0

    def expects(self, line):

        ret = False

        if self._mod == 0:
            if not self._decay():
                return False
            ret = line.startswith(">")
        elif self._mod == 1:
            ret = bool(re.match(self.MATCH_AA, line) or re.match(self.MATCH_NT))
        elif self._mod == 2:
            ret = line.startswith("+")
        elif self._mod == 3:
            ret = self._qualExpect()
        self._next()
        return ret
    

class SeqFormatDetector(object):

    FORMATS = [Fasta, FastaMultiline, FastQ]

    def __init__(self, forceFormat=None):

        self._safetyCheck = None

        self._format = None
        self._itemSize = None
        self._hasSequence = None
        self._hasQuality = None
        self._qualityEncoding = None
        self._possibleFormats = [f() for f in self.FORMATS]

    @property
    def detecting(self):

        return self._format is None

    @property
    def itemSize(self):

        return self._itemSize

    @property
    def qualityEncoding(self):
        
        return self._qualityEncoding

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

        return ((not encoder.useSequence or self.hasSeqence) and
                (not encoder.useQuality or self.hasQuality))

    def feed(self, line):

        self._possibleFormats = [f for f in self._possibleFormats if
                f.expects(line)]
        
        l = len(self._possibleFormats)

        if l == 0:
            raise FormatError("Unknown format, no known formats left")
        elif l == 1:
            f = self._possibleFormats[0]
            if self._safetyCheck is None:
                self._safetyCheck = f.itemSize
            elif self._safetyCheck > 0:
                self._safetyCheck -= 1
            elif self._testFormatInformative(f):
                self._itemSize = f.itemSize
                self._hasSequence = f.hasSeqence
                self._hasQuality = f.hasQuality
                self._qualityEncoding = f.qualityEncoding
                self._format = f.name

        return self
