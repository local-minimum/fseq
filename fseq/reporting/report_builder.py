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


class ReportBuilderPositionAverage(ReportBuilderBase):

    def __init__(self, outputRoot=None, outputNamePrefix=None,
                 undecidedValue=0.5, *reports):

        super(ReportBuilderPositionAverage, self).__init__(
            outputRoot=outputRoot, outputNamePrefix=outputNamePrefix,
            *reports)

        self.undecidedValue = undecidedValue

    @property
    def undecidedValue(self):
        return self._undecidedValue

    @undecidedValue.setter
    def undecidedValue(self, val):
        self._undecidedValue = val

    def _floatBin(self, C):

        u = np.unique(C)
        return np.histogram(C, bins=np.hstack((np.unique(C), (np.inf,))))

    def _getF(self, X, Y, val):

        if val not in Y:
            return 0

        return X[Y[:X.size] == val] / X.sum().astype(np.float)

    def _getNotF(self, X, Y, val):

        pos = Y[:X.size] != val
        return (X[pos] * Y[pos]).sum() / X.sum().astype(np.float)

    def distill(self, data, undecidedValue=None, *args, **kwargs):
        """The distiller will create reports for several position-type
        informations.

        Average Lacking Data Frequency
            The number of undecided values.

        Average Non-Lacking Data
            The per position average for all non-lacking data values.

        Average Combined Data
            The per position average as encoded.


        Parameters
        ----------

        data: numpy.ndarray
            An array of numerically encoded sequence information

        undecidedValue: float, optional
            The value that undecided sequence positions are encoded as.
            If not supplied, the previously set value of the class instance
            will be used.
            (Default: 0.5)

        *args:
            Any args will be passed to the `ReportBuilderBase.distill`

        **kwargs:
            Any kwargs will be passed to the `ReportBuilderBase.distill`
            ..note:: `outputNamePrefix` will be overwritten/added

        Returns
        -------

        fseq.ReportBuilderPositionAverage
            Returns `self`
        """
        
        if undecidedValue is None:
            undecidedValue = self.undecidedValue

        super(ReportBuilderPositionAverage, self).distill(
            data.mean(axis=0, dtype=np.float),
            outputNamePrefix='average.total.', *args, **kwargs)

        freqs, bins = zip(*(self._floatBin(C) for C in data.T))
        undecidedV = np.ones_like(freqs) * undecidedValue

        lacking = np.frompyfunc(self._getF, 3, 1)

        super(ReportBuilderPositionAverage, self).distill(
            lacking(freqs, bins, undecidedV),
            outputNamePrefix='average.lacking.', *args, **kwargs)
    
        notLacking = np.frompyfunc(self._getF, 3, 1)

        super(ReportBuilderPositionAverage, self).distill(
            notLacking(freqs, bins, undecidedV),
            outputNamePrefix='average.not-lacking.', *args, **kwargs)
