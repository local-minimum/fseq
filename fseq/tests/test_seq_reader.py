#!/usr/bin/env python
"""These tests only test the aspects of the `fseq.SeqReader` that does not
involve running the the encoding as that behaviour is a complex behaviour
involving all aspects of `fseq` those tests are performed by `test_fseq`.

Those are:

    SeqReader.run()

    for res in SeqReader
        ...

    SeqReader.clearResults()

    SeqReader.next()

    SeqReader.reportDirectory

    SeqReader.results

However the `SeqReader.run()` is tested for raising exception when no
encoder is present.

"""

import unittest

from fseq import SeqReader, SeqEncoder, ReportBuilderBase


class TestSeqReader(unittest.TestCase):

    def setUp(self):

        self._mockSources = ['foo/bar.fasta', 'foo/foo/bar.fastq']
        self._mockTargets = ['reports', 'Reports']

    def test_noDataSource(self):

        s = SeqReader()
        self.assertEqual(len(s), 0)

    def test_addDataSourceStart(self):

        s = SeqReader(dataSourcePaths=self._mockSources)

        self.assertEqual(len(s), len(self._mockSources))

        self.assertEqual(zip(*s.jobQueue)[0], tuple(self._mockSources))

        s = SeqReader(dataSourcePaths=self._mockSources[0])

        self.assertEqual(len(s), 1)

    def test_addDataSource(self):

        s = SeqReader()

        s.addData(self._mockSources)

        self.assertEqual(len(s), len(self._mockSources))

        self.assertEqual(zip(*s.jobQueue)[0], tuple(self._mockSources))

        s = SeqReader()

        s.addData(self._mockSources[0])

        self.assertEqual(zip(*s.jobQueue)[0], (self._mockSources[0], ))

    def test_addDataSourceTargetStart(self):

        s = SeqReader(dataSourcePaths=self._mockSources,
                      dataTargetPaths=self._mockTargets)

        self.assertEqual(len(s), len(self._mockSources))

        sources, targets = zip(*s.jobQueue)

        self.assertEqual(sources, tuple(self._mockSources))
        self.assertEqual(targets, tuple(self._mockTargets))

    def test_encoder(self): 

        e1 = SeqEncoder()

        s = SeqReader(seqEncoder=e1)

        self.assertEqual(s.seqEncoder, e1)

    def test_encoderFails(self):

        s = SeqReader()

        with self.assertRaises(TypeError):
            s.seqEncoder = None
        with self.assertRaises(TypeError):
            s.seqEncoder = 1
        with self.assertRaises(TypeError):
            s.seqEncoder = u"dafjk"
        with self.assertRaises(TypeError):
            s.seqEncoder = s
        with self.assertRaises(TypeError):
            SeqReader(seqEncoder=u"asfs")

    def test_encoderReplace(self):
        e1 = SeqEncoder()
        e2 = SeqEncoder()
        s = SeqReader(seqEncoder=e1)
        
        s.seqEncoder = e2

        self.assertEqual(s.seqEncoder, e2)

    def test_allRunFails(self):

        s = SeqReader()

        with self.assertRaises(ValueError):
            for res in s:
                pass

        self.assertRaises(ValueError, s.run)

        self.assertRaises(ValueError, s.next)

    def test_reportBulder(self):

        rb = ReportBuilderBase()
        rb2 = ReportBuilderBase()

        s = SeqReader(reportBuilder=rb)

        self.assertEqual(len(tuple(s.reportBuilders)), 1)
        self.assertEqual(tuple(s.reportBuilders)[0], rb)

        s.addReportBuilder(rb2)

        self.assertEqual(len(tuple(s.reportBuilders)), 2)

    def test_ReportBuilderBaseRemoval(self):

        rb = ReportBuilderBase()
        rb2 = ReportBuilderBase()

        s = SeqReader(reportBuilder=rb)
        s.addReportBuilder(rb2)
        s.removeReportBuilders(rb)
        
        self.assertEqual(len(tuple(s.reportBuilders)), 1)
        self.assertEqual(tuple(s.reportBuilders)[0], rb2)

        s.addReportBuilder(rb)
        s.removeReportBuilders(rb, rb2)
        self.assertEqual(len(tuple(s.reportBuilders)), 0)

        s.addReportBuilder(rb)
        s.addReportBuilder(rb2)
        s.removeReportBuilders()
        self.assertEqual(len(tuple(s.reportBuilders)), 0)

    def test_reportBulderFail(self):

        s = SeqReader()
        rbs = (ReportBuilderBase(), ReportBuilderBase())

        self.assertRaises(TypeError, s.addReportBuilder, None)
        self.assertRaises(TypeError, s.addReportBuilder, True)
        self.assertRaises(TypeError, s.addReportBuilder, 1)
        self.assertRaises(TypeError, s.addReportBuilder, "adsf")
        self.assertRaises(TypeError, s.addReportBuilder, rbs)

    def test_popDataSources(self):

        s = SeqReader()
        self.assertEqual(s.popDataSources, True)

        s.popDataSources = False
        self.assertEqual(s.popDataSources, False)

        s = SeqReader(popDataSources=False)
        self.assertEqual(s.popDataSources, False)

    def test_resetSeqEncoder(self):

        s = SeqReader()

        self.assertEqual(s.resetSeqEncoder, True)

        s.resetSeqEncoder = False

        self.assertEqual(s.resetSeqEncoder, False)

        s = SeqReader(resetSeqEncoder=False)

        self.assertEqual(s.resetSeqEncoder, False)

    def test_popEncodingResultsDefault(self):

        s = SeqReader()

        self.assertEqual(s.popEncodingResults, True)

        s = SeqReader(dataSourcePaths=self._mockSources)

        self.assertEqual(s.popEncodingResults, True)

        s = SeqReader(dataSourcePaths=self._mockSources[0])

        self.assertEqual(s.popEncodingResults, False)

    def test_popEncodingResultsManual(self):

        s = SeqReader(popEncodingResults=False)

        self.assertEqual(s.popEncodingResults, False)

        s = SeqReader(popEncodingResults=False,
                      dataSourcePaths=self._mockSources)

        self.assertEqual(s.popEncodingResults, False)

        s = SeqReader(popEncodingResults=True,
                      dataSourcePaths=self._mockSources[0])

        self.assertEqual(s.popEncodingResults, True)

    def test_results(self):

        s = SeqReader()

        self.assertEqual(list(s.results), [])

    def test_reportDirectory(self):

        s = SeqReader()
        self.assertEqual(s.reportDirectory, '')

if __name__ == '__main__':
    unittest.main()
