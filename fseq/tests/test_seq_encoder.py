#!/usr/bin/env python

import unittest
import random

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
            isinstance(getattr(fseq.SeqFormat, p), property))

    def test_baseExpects(self):

        for d in self._invalidDataType:
            self.assertRaises(fseq.FormatImplementationError,
                    self._baseFormat.expects, d)

    def test_baseProperties(self):

        for p in self._baseProperties:

            self.assertIsNone(getattr(self._baseFormat, p))

    def test_derivdedFormatExpects(self):

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

    def test_propertiesNotNameInformative(self):

        notName = set(self._baseProperties).difference(['name'])
        notInformative = {None}

        for f in self._derivedFormats:

            self.assertNotEqual(set(getattr(f, p) for p in notName),
                                notInformative)

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



                
