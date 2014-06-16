#!/usr/bin/env python
"""The report builders are classes that coordinate report productions"""

import warnings
import numpy as np


class ReportBuilderBase(object):

    def __init__(self, outputRoot=None, outputNamePrefix=None, *reports):

        self._reports = set()
        self.outputRoot=outputRoot
        self.outputNamePrefix=outputNamePrefix 
        self.addReports(*reports)

    @property
    def outputNamePrefix(self):
        """Partial file name to prepend the individual reports: str"""

        return self._outputNamePrefix

    @outputNamePrefix.setter
    def outputNamePrefix(self, val):

        self._outputNamePrefix = val

    @property
    def outputRoot(self):
        """The base for saving out reports: str"""

        return self._outputRoot

    @outputRoot.setter
    def outputRoot(self, val):

        if val is None:
            val = ''

        self._outputRoot = str(val)

    def addReports(self, *reports):
        """Adds any number of reports given that the reports exposes a 
        distill method.

        Parameters
        ----------
        
        *reports: objects, optional

        Returns
        -------

        fseq.ReportBuilderBase
            Returns `self`
        """

        for r in reports:

            if r not in self._reports:
                if hasattr(r, 'distill'):
                    self._reports.add(r)
                else:
                    raise ValueError("{0} lacks distill-method".format(r))
            else:
                warnings.warn("{0} already in reports...omitting.".format(r))

        return self

    def distill(self, *args, **kwargs):
        """The base distiller will not process any data passed to it,
        it will send all arguments and keyword arguments to the individual
        reports.

        If either `outputRoot` or `outputNamePrefix` are passed as kwargs,
        the corresponding values preset in the system will be added to the
        kwargs sent to the subreports.

        Returns
        -------

        fseq.ReportBuilderBase
            Returns `self`
        """
        for k in ('outputRoot', 'outputNamePrefix'):
            if k not in kwargs:
                kwargs[k] = getattr(self, k) 

        for r in self._reports:
            r.distill(*args, **kwargs)

        return self
