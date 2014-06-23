#!/usr/bin/env python

import unittest

import fseq

class TestGenericBuilder(unittest.TestCase):

    def setUp(self):

        self._builderConstructor = fseq.ReportBuilderBase
        self._startReports = 0

    def test_empty(self):

        rb = self._builderConstructor()

        self.assertEqual(rb.outputRoot, '')

        self.assertEqual(len(rb), self._startReports)

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

        self.assertEqual(len(rb), self._startReports + 1)

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

    def setUp(self):

        self._builderConstructor = fseq.ReportBuilderFFT
        self._startReports = 1

    def test_sampleSize(self):

        self.assertEqual(self._builderConstructor(sampleSize=50).sampleSize, 50)

        rb = self._builderConstructor()

        rb.sampleSize = 2000

        self.assertEqual(rb.sampleSize, 2000)

    def test_distanceMetirc(self):

        self.assertIn(self._builderConstructor().distanceMetric,
                      self._builderConstructor.METRICS)

        m2 = None
        for i, m in enumerate(self._builderConstructor.METRICS):
            rb = self._builderConstructor(distanceMetric=m)
            self.assertEqual(rb.distanceMetric, m)
            if m2 is not None:
                rb.distanceMetric = m2
                self.assertEqual(rb.distanceMetric, m2)
            m2 = m

        
class TestAverageBuilder(TestGenericBuilder):

    def setUp(self):

        self._builderConstructor = fseq.ReportBuilderPositionAverage
        self._startReports = 1

    def test_undecidedValue(self):

        self.assertEqual(self._builderConstructor().undecidedValue, 0.5)

        rb = self._builderConstructor(undecidedValue=-1)

        self.assertEqual(rb.undecidedValue, -1)

        rb.undecidedValue = 0.5

        self.assertEqual(rb.undecidedValue, 0.5)
