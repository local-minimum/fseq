#!/usr/bin/env python

import unittest

import fseq

class TestGenericBuilder(unittest.TestCase):

    def setUp(self):

        self._builderConstructor = fseq.ReportBuilderBase

    def test_empty(self):

        rb = self._builderConstructor()

        self.assertEqual(rb.outputRoot, '')

        self.assertEqual(len(rb), 0)

    def test_raisesBadReport(self):

        rb = self._builderConstructor()

        self.assertRaises(ValueError, rb.addReports, [])

    def test_addReportsFromStart(self):

        rb = self._builderConstructor(fseq.LinePlot())

        self.assertEqual(len(rb), 1)

        rb = self._builderConstructor(fseq.LinePlot(), fseq.LinePlot(),
                                    fseq.HeatMap())

        self.assertEqual(len(rb), 3)

    def test_addReport(self):

        rb = self._builderConstructor()
        rb.addReports(fseq.HeatMap())

        self.assertEqual(len(rb), 1)

    def test_setPrefix(self):

        pref1 = 'test'
        pref2 = 'anothertest'

        self.assertEqual(self._builderConstructor().outputNamePrefix, None)

        rb = self._builderConstructor(outputNamePrefix=pref1)

        self.assertEqual(rb.outputNamePrefix, pref1)

        rb.outputNamePrefix = pref2

        self.assertEqual(rb.outputNamePrefix, pref2)

    def test_setRoot(self):

        root1 = '.'
        root2 = 'test/'

        self.assertEqual(self._builderConstructor().outputRoot, '')

        rb = self._builderConstructor(outputRoot=root1)

        self.assertEqual(rb.outputRoot, root1)

        rb.outputRoot = root2

        self.assertEqual(rb.outputRoot, root2)


class TestFFTBulder(TestGenericBuilder):

    def setup(self):

        self._builderConstructor = fseq.ReportBuilderFFT


class TestAverageBuilder(TestGenericBuilder):

    def setup(self):

        self._builderConstructor = fseq.ReportBuilderPositionAverage
