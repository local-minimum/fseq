#!/usr/bin/env python

import unittest

import fseq


class TestReports(unittest.TestCase):

    def setUp(self):

        pass

    def test_name(self):

        n1 = 'test'
        n2 = 'test2'

        r = fseq.ReportBase()

        self.assertEqual(r.name, None)

        r = fseq.ReportBase(name=n1)

        self.assertEqual(r.name, n1)

        r.name = n2

        self.assertEqual(r.name, n2)

    def test_saveArgs(self):

        a1 = (1, 2)
        a2 = ('a', 'b')

        r = fseq.ReportBase()

        self.assertEqual(r.saveArgs, tuple())

        r = fseq.ReportBase(saveArgs=a1)

        self.assertEqual(r.saveArgs, a1)

        r.saveArgs = a2

        self.assertEqual(r.saveArgs, a2)
        
    def test_saveKwargs(self):

        a1 = {'a': 1} 
        a2 = {'b': 2}

        r = fseq.ReportBase()

        self.assertEqual(r.saveKwargs, dict())

        r = fseq.ReportBase(saveKwargs=a1)

        self.assertEqual(r.saveKwargs, a1)

        r.saveKwargs = a2

        self.assertEqual(r.saveKwargs, a2)
        
    def test_goodReport(self):

        r = fseq.ReportBase()

        rb = fseq.ReportBuilderBase()
        
        rb.addReports(r)

        self.assertIn(r, rb)

    def test_distillRaises(self):

        self.assertRaises(NotImplementedError, fseq.ReportBase().distill, None)

