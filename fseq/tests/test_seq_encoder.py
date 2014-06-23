#!/usr/bin/env python

import unittest
import random
import os
import numpy as np

import fseq

def discoverSubclasses(cls):
    """Returns a list of all classes derived from the the supplied base
    class.
    
    Implementation based on ubuntu's answer to related question on
    StackOverflow [1]_.

    Parameters
    ----------

    cls: type
        The base to search from

    Returns
    -------

    list
        List of all classes that uses `cls` directly or indirectly.

    References
    ----------

    ..[1] "How can I find all subclasses of a given class in Python?"
    http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python
    """

    return cls.__subclasses__() + [g for s in cls.__subclasses__() for
                                   g in discoverSubclasses(s)]


class TestSeqFormats(unittest.TestCase):
    """Testing all sequence formats and testing of the base class `SeqFormat`"""

    def setUp(self):

        self._derivedFormats = tuple(f() for f in 
                                     discoverSubclasses(fseq.SeqFormat))

        self._baseFormat = fseq.SeqFormat()
        self._validDataType = (">Help", "ADASF", "asdf", "+agf", "---sdfa2356")
        self._invalidDataType = (1, 1.2, None, False, True, [">", "ad"], {})
        self._comboData = self._invalidDataType + self._validDataType
        self._baseProperties = tuple(
            p for p in set(vars(fseq.SeqFormat)).difference(vars(object)) if
            isinstance(getattr(fseq.SeqFormat, p), property) and
            p not in {'givenUp'})

        self._baseDir = os.path.abspath(os.path.dirname(__file__))

    def test_baseExpects(self):

        for d in self._invalidDataType:
            self.assertRaises(fseq.FormatImplementationError,
                    self._baseFormat.expects, d)

    def test_baseProperties(self):

        for p in self._baseProperties:

            self.assertIsNone(getattr(self._baseFormat, p))

    def test_derivedFormatExpects(self):

        for f in self._derivedFormats:

            for d in self._comboData:
                try:
                    f.expects(d)
                except fseq.FormatImplementationError:
                    self.fail("{0} exposes {1} when supplied with {2}".format(
                        d, self._baseFormat.expects, d))
                except:
                    pass

    def test_invalidData(self):


        for f in self._derivedFormats:

            for _ in range(1000):

                try:
                    d = random.sample(self._invalidDataType, 1)[0]
                    if f.expects(d):
                        self.fail("{0} returned `True` for {1}".format(
                            f, d)) 
                except:

                    pass

    def test_named(self):

        for f in self._derivedFormats:

            n = f.name
            self.assertIsInstance(n, str)
            self.assertNotEqual(len(n), 0)

    def test_uniqueNames(self):

        names = [f.name for f in self._derivedFormats]
        self.assertEqual(len(names), len(set(names)),
                         msg="All names are not unique")

    def test_propertiesNotNameInformative(self):

        notName = set(self._baseProperties).difference(['name'])
        notInformative = {None}

        for f in self._derivedFormats:

            self.assertNotEqual(set(getattr(f, p) for p in notName),
                                notInformative)

    def test_propertiesAreInformative(self):

        for f in self._derivedFormats:

            if f.hasSequence:
                self.assertNotEqual(f.SEQUENCE_LINE, None)
            if f.hasQuality:
                self.assertNotEqual(f.HEADER_LINE, None)

    def test_itemSize(self):

        itemSizes = {type(None), int}

        for f in self._derivedFormats:

            i = f.itemSize
            self.assertIn(type(i), itemSizes)
            
    def test_qualityEncoding(self):

        for f in self._derivedFormats:

            qe = f.qualityEncoding
            if qe is not None and not hasattr(qe, "__getitem__"):
                self.fail(
                    "{0} has invalid type of quality encoding {1}".format(
                        f, qe))

    def test_singlelineFasta(self):

        fastaS = fseq.FastaSingleline()
        fastaM = fseq.FastaMultiline()
        fastQ = fseq.FastQ()

        fQres = []

        with open(os.path.join(
                self._baseDir, 'data/singlelineProt.fasta'), 'r') as fs:

            for i, line in enumerate(fs):
                msg = "{0} did not return {1}\n" + "{0}: {1}".format(i + 1, line)
                self.assertTrue(fastaS.expects(line), msg=msg.format(
                    type(fastaS), True))
                if not fastaM.givenUp:
                    self.assertTrue(fastaM.expects(line), msg=msg.format(
                        type(fastaM), True))
                else:
                    self.assertFalse(fastaM.expects(line), msg=msg.format(
                        type(fastaM), False))

                fQres.append(fastQ.expects(line))

        self.assertIn(False, fQres)

    def test_multilineFasta(self):

        for p in ('data/multilineNT.fasta', 'data/multilineProt.fasta'):

            fastaS = fseq.FastaSingleline()
            fastaM = fseq.FastaMultiline()
            fastQ = fseq.FastQ()

            fQres = []
            fSres = []

            with open(os.path.join(
                    self._baseDir, p), 'r') as fs:

                for i, line in enumerate(fs):
                    msg = "{0} did not return {1}\n" + "{0}: {1}".format(i + 1, line)
                    if not fastaM.givenUp:
                        self.assertTrue(fastaM.expects(line), msg=msg.format(
                            type(fastaM), True))
                    else:
                        self.assertFalse(fastaM.expects(line), msg=msg.format(
                            type(fastaM), False))

                    fQres.append(fastQ.expects(line))
                    fSres.append(fastaS.expects(line))

            self.assertIn(False, fQres)
            self.assertIn(False, fSres)

    def test_fastq(self):

        for p in ('data/NT.fastq',):

            fastaS = fseq.FastaSingleline()
            fastaM = fseq.FastaMultiline()
            fastQ = fseq.FastQ()

            fMres = []
            fSres = []

            with open(os.path.join(
                    self._baseDir, p), 'r') as fs:

                for i, line in enumerate(fs):
                    msg = "{0} did not return {1}\n" + "{0}: {1}".format(i + 1, line)
                    if not fastQ.givenUp:
                        self.assertTrue(fastQ.expects(line), msg=msg.format(
                            type(fastQ), True))
                    else:
                        self.assertFalse(fastQ.expects(line), msg=msg.format(
                            type(fastQ), False))

                    fMres.append(fastaM.expects(line))
                    fSres.append(fastaS.expects(line))

            self.assertIn(False, fMres)
            self.assertIn(False, fSres)


class TestSeqFormatDetector(unittest.TestCase):


    def setUp(self):
        self._baseDir = os.path.abspath(os.path.dirname(__file__))

    def test_startDetecting(self):

        d = fseq.SeqFormatDetector()

        self.assertTrue(d.detecting)

    def test_startForcedDetecting(self):

        fq = fseq.FastQ()

        d = fseq.SeqFormatDetector()

        self.assertTrue(d.detecting)

    def test_ForcedFormat(self):

        fq = fseq.FastQ()

        d = fseq.SeqFormatDetector(forceFormat=fq)

        try:
            with open(os.path.join(self._baseDir, "data/NT.fastq")) as fs:

                for line in fs:

                    if not d.detecting:
                        break

                    d.feed(line)

        except fseq.FormatUnknown:

            self.fail("FastQ was not detected")

        self.assertFalse(d.detecting)
        self.assertEqual(d.format, fq.name)
        self.assertEqual(d.itemSize, fq.itemSize)
        self.assertEqual(d.hasQuality, fq.hasQuality)
        self.assertEqual(d.hasSequence, fq.hasSequence)
        self.assertEqual(d.qualityEncoding, fq.qualityEncoding)

    def test_Format(self):

        fq = fseq.FastQ()

        d = fseq.SeqFormatDetector()

        try:
            with open(os.path.join(self._baseDir, "data/NT.fastq")) as fs:

                for line in fs:

                    if not d.detecting:
                        break

                    d.feed(line)

        except fseq.FormatUnknown:

            self.fail("FastQ was not detected")

        self.assertFalse(d.detecting)
        self.assertEqual(d.format, fq.name)

    def test_FormatUnknown(self):

        d = fseq.SeqFormatDetector()

        self.assertRaises(fseq.FormatUnknown, d.feed, "14124daf")

        fq = fseq.FastQ()
        
        d = fseq.SeqFormatDetector(forceFormat=fq)

        self.assertRaises(fseq.FormatUnknown, d.feed, ">someFasta")

    def test_compatible(self):

        fq = fseq.FastQ()

        d = fseq.SeqFormatDetector()

        with open(os.path.join(self._baseDir, "data/NT.fastq")) as fs:

            for line in fs:

                if not d.detecting:
                    break

                d.feed(line)
        
        e = fseq.SeqEncoder()

        self.assertTrue(d.compatible(e))

        e.useQuality = True

        self.assertTrue(d.compatible(e))

    def test_compatibleException(self):

        fq = fseq.FastQ()

        d = fseq.SeqFormatDetector()

        e = fseq.SeqEncoder()

        self.assertRaises(fseq.FormatError, d.compatible, e)

    def test_compatibleFasta(self):

        f = fseq.FastaSingleline()

        d = fseq.SeqFormatDetector()

        with open(os.path.join(
                self._baseDir, 'data/singlelineProt.fasta'), 'r') as fs:

            for line in fs:

                if not d.detecting:
                    break

                d.feed(line)

        self.assertEqual(d.format, f.name) 

        e = fseq.SeqEncoder()

        self.assertTrue(d.compatible(e))

        e.useQuality = True

        self.assertFalse(d.compatible(e))

    
class TestEncoder(unittest.TestCase):


    def test_useSequence(self):

        e = fseq.SeqEncoder()

        self.assertTrue(e.useSequence)

        e.useSequence = False

        self.assertFalse(e.useSequence)

        e.useSequence = True

        self.assertTrue(e.useSequence)

    def test_useQuality(self):

        e = fseq.SeqEncoder()

        self.assertFalse(e.useQuality)

        e.useQuality = True

        self.assertTrue(e.useQuality)

        e.useQuality = False

        self.assertFalse(e.useQuality)

    def test_seqEncoding(self):

        self.assertIs(fseq.SeqEncoder().sequenceEncoding, None)

        se = {}

        e = fseq.SeqEncoder(sequenceEncoding=se)

        self.assertIs(e.sequenceEncoding, se)

        se = {'A': 1}

        e.sequenceEncoding = se

        self.assertIs(e.sequenceEncoding, se)

        with self.assertRaises(TypeError):
            e.sequenceEncoding = []

    def test_qualEncoding(self):

        self.assertIs(fseq.SeqEncoder().qualityEncoding, None)

        qe = {}
        e = fseq.SeqEncoder(qualityEncoding=qe)

        self.assertIs(e.qualityEncoding, qe)

        qe = {'a': 1}

        e.qualityEncoding = qe

        self.assertIs(e.qualityEncoding, qe)

        with self.assertRaises(TypeError):
            e.qualityEncoding = []

    def test_expectedFormat(self):

        e = fseq.SeqEncoder()

        self.assertIs(e.format, None)

        f = fseq.FastQ()

        e = fseq.SeqEncoder(expectedInputFormat=f)

        self.assertIsInstance(e.format, fseq.SeqFormatDetector)

        self.assertEqual(e.format.format, f.name)

        self.assertTrue(e.initiated)

    def test_reset(self):

        e = fseq.SeqEncoder(expectedInputFormat=fseq.FastQ())

        e.reset()

        self.assertFalse(e.initiated)

        self.assertIs(e.format, None)

    def test_parseRaises(self):

        with self.assertRaises(NotImplementedError):
            fseq.SeqEncoder().parse(None, None, None)
        

class TestEncoderQC(unittest.TestCase):

    
    def setUp(self):

        self._eQC = fseq.SeqEncoderGC(
            expectedInputFormat=fseq.FastaSingleline())

        self._spoofHead=">Read1"
        self._out = np.zeros((11, 101)) * -1

    def test_putRightRow(self):

        for row in (4, 3, 7, 0):

            l = "".join(
                [random.sample(['A', 'T', 'C', 'G', 'N'], 1)[0] for
                    _ in range(101)])

            self._eQC.parse([self._spoofHead, l], self._out, row)

            for col, c in enumerate(l):
                self.assertEqual(self._eQC.sequenceEncoding[c],
                                 self._out[row, col])

    def test_correctLengthG(self):

        self._eQC.parse([self._spoofHead, 'G'*101], self._out, 0)
        
        np.testing.assert_allclose(self._out[0], 1)
        
    def test_shortLengthG(self):

        l = 50
        self._eQC.parse([self._spoofHead, 'G'*l], self._out, 6)
        
        np.testing.assert_allclose(self._out[6, :l], 1)
        np.testing.assert_allclose(self._out[6, l:], -1)

    def test_longLengthG(self):

        l = 1000
        self._eQC.parse([self._spoofHead, 'G'*l], self._out, 5)
        
        np.testing.assert_allclose(self._out[5], 1)

    def test_C(self):

        self._eQC.parse([self._spoofHead, 'C'*101], self._out, 1)
        
        np.testing.assert_allclose(self._out[1], 1)

    def test_A(self):

        self._eQC.parse([self._spoofHead, 'A'*101], self._out, 8)
        
        np.testing.assert_allclose(self._out[8], 0)

    def test_T(self):

        self._eQC.parse([self._spoofHead, 'T'*101], self._out, 9)
        
        np.testing.assert_allclose(self._out[9], 0)

    def test_N(self):

        self._eQC.parse([self._spoofHead, 'N'*101], self._out, 10)
        
        np.testing.assert_allclose(self._out[10], 0.5)


if __name__ == '__main__':
    unittest.main()
