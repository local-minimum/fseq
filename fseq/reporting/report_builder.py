#!/usr/bin/env python
"""The report builders are classes that coordinate report productions"""

import warnings
import numpy as np

import scipy.spatial.distance as dist
import scipy.cluster.hierarchy as hier

import fseq


class ReportBuilderBase(object):
    """Base class for common report builder features.

    Most prominently, the distill-method needs to be implemented in
    subclasses to make much sence in most use cases.

    Parameters
    ----------

    outputRoot: str, optional
        Path to the directory where all reports should be put

        (Default: ``None``)

    outputNamePrefix: str, optional
        Partial name to be added to all reports done by the builder

        (Default: ``None``)

    *reports: objects, optional
        Any number of reports to be added from start

    Attributes
    ----------

    outputRoot
    outputNamePrefix
    DEFAULT_REPORTS
    """

    DEFAULT_REPORTS = tuple()

    def __init__(self, *reports, **kwargs):
        """
        Parameters
        ----------

        outputRoot: str, optional
            Path to the directory where all reports should be put

            (Default: ``None``)

        outputNamePrefix: str, optional
            Partial name to be added to all reports done by the builder

            (Default: ``None``)

        *reports: objects, optional
            Any number of reports to be added from start
        """

        self._reports = set()

        if len(reports) == 0:
            reports = tuple(r() for r in self.DEFAULT_REPORTS)

        self.outputRoot='outputRoot' in kwargs and kwargs['outputRoot'] or None
        self.outputNamePrefix='outputNamePrefix' in kwargs and \
            kwargs['outputNamePrefix'] or None
        self.addReports(*reports)

    def __len__(self):

        return len(self._reports)

    def __iter__(self):

        return iter(self._reports)

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
            Returns ``self``

        Raises
        ------

        ValueError
            If a report lacks a method named ``distill`` or can't be hashed
        """

        for r in reports:

            if hasattr(r, 'distill') and r.__hash__ is not None:
                if r in self._reports:
                    warnings.warn(
                        "{0} already in reports...omitting.".format(r))
                self._reports.add(r)
            else:
                raise ValueError(
                    "{0} lacks distill-method or not hashable".format(r))

        return self

    def distill(self, *args, **kwargs):
        """The base distiller will not process any data passed to it,
        it will send all arguments and keyword arguments to the individual
        reports.

        If either ``outputRoot`` or ``outputNamePrefix`` are passed as kwargs,
        the corresponding values preset in the system will be added to the
        kwargs sent to the subreports.

        Returns
        -------

        fseq.ReportBuilderBase
            Returns ``self``
        """
        for k in ('outputRoot', 'outputNamePrefix'):
            if k not in kwargs:
                kwargs[k] = getattr(self, k) 

        for r in self._reports:
            r.distill(*args, **kwargs)

        return self

class ReportBuilderFFT(ReportBuilderBase):
    """Samples part of data set and performs FFT-based analysis on it.

    Parameters
    ----------

    outputRoot: str, optional
        Path to the directory where all reports should be put

        (Default: ``None``)

    outputNamePrefix: str, optional
        Partial name to be added to all reports done by the builder

        (Default: ``None``)

    sampleSize: int, optional
        Size of sample to be randomly drawn
        
        (Default: 1000)

    distanceMetric: str, optional
        Name of distance metric to be used.
        See ``METRICS``-attribute for allowed metrics.

        (Default: 'correlation')

    *reports: objects, optional
        Any number of reports to be added from start

        (Default: A fseq.HeatMap)

    Attributes
    ----------

    distanceMetric
    sampleSize

    See also
    --------

    ReportBuilderBase
        Base class implementing more attributes.
    """

    METRICS = {'braycurtis', 'canberra', 'chebyshev', 'cityblock',
               'correlation', 'cosine', 'dice', 'euclidean', 'hamming',
               'jaccard', 'kulsinski', 'mahalanobis', 'matching',
               'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean',
               'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule'}

    DEFAULT_REPORTS = (fseq.HeatMap, )

    def __init__(self, *reports, **kwargs):
        """
        Parameters
        ----------

        outputRoot: str, optional
            Path to the directory where all reports should be put

            (Default: ``None``)

        outputNamePrefix: str, optional
            Partial name to be added to all reports done by the builder

            (Default: ``None``)

        sampleSize: int, optional
            Size of sample to be randomly drawn
            
            (Default: 1000)

        distanceMetric: str, optional
            Name of distance metric to be used.
            See ``ReportBuilderFFT.METRICS``_ for allowed metrics.

            (Default: 'correlation')

        *reports: objects, optional
            Any number of reports to be added from start

            (Default: A fseq.HeatMap)
        """

        if len(reports) == 0:
            reports = tuple(r() for r in self.DEFAULT_REPORTS)

        super(ReportBuilderFFT, self).__init__(
            *reports, **kwargs)

        self.sampleSize = 'sampleSize' in kwargs and kwargs['sampleSize'] or \
            1000
        self.distanceMetric = 'distanceMetric' in kwargs and \
            kwargs['distanceMetric'] or 'correlation'

    @property
    def distanceMetric(self):
        """The ReportBuilderFFT.METRIC used: str"""
        return self._distanceMetric

    @distanceMetric.setter
    def distanceMetric(self, metric):

        metric = metric.lower()
        if metric in self.METRICS:
            self._distanceMetric = metric
        else:
            raise ValueError("{0} not a valid metric ({1})".format(
                metric, self.METRICS))

    @property
    def sampleSize(self):
        """Size of data subsample to analyze: int"""
        return self._sampleSize

    @sampleSize.setter
    def sampleSize(self, val):

        self._sampleSize = val
    
    def _getLeafOrder(self, A, metric, w=None, V=None, VI=None):

        distMatrix = dist.pdist(A, metric=metric, w=w, V=V, VI=VI)

        distSquareM = dist.squareform(distMatrix)

        linkageM = hier.linkage(distSquareM)

        dendro = hier.dendrogram(linkageM)

        return dendro['leaves'] 


    def distill(self, data, distanceMetric=None, clusterOnAbsOnly=True,
            *args, **kwargs):
        """Make reports from data.

        Produces two analyses:

        Amplitude evaluation
            A clustered FFT-amplitude analysis

        Angle evaluation
            A clustered FFT-angle analysis

        Parameters
        ----------

        data: numpy.ndarray
            The 2D-array of data given

        distanceMetric: str, optional
            A distance metric to overwrite the default one of the instance.

            (Default: Value of ``self.distanceMetric``)
            
        clusterOnAbsOnly: bool, optional
            If clustering should be performed only on the amplitude (abs-values)
            or if amplitude and angle be clustered independently.

            (Default: Cluster only on amplitude)
        """
        if distanceMetric is None:
            distanceMetric = self.distanceMetric

        D = np.arange(data.shape[0])
        np.random.shuffle(D)
        data = data[D[:self.sampleSize]]

        fD = np.fft.rfft(data, axis=1)

        A = np.abs(fD)
        V = np.std(A, axis=0) 
        O = self._getLeafOrder(A, distanceMetric, V=V)

        super(ReportBuilderFFT, self).distill(
            A[O],
            outputNamePrefix='fft-sample.abs.',
            title='absolute FFT values for {0} random sample sequences'.format(
                self.sampleSize),
            xlabel='Frequency',
            ylabel='Read n',
            axisOff=False,
            *args, **kwargs)

        #A = (np.angle(fD) - np.angle(fD[:, :1])) % (2 * np.pi)
        A = np.angle(fD)
        V = np.std(A, axis=0) 
        if not clusterOnAbsOnly:
            O = self._getLeafOrder(A, distanceMetric, V=V)
        
        super(ReportBuilderFFT, self).distill(
            A[O],
            outputNamePrefix='fft-sample.angle.',
            title='FFT angle for {0} random sample sequences'.format(
                self.sampleSize),
            xlabel='Frequency',
            ylabel='Read n',
            axisOff=False,
            *args, **kwargs)


class ReportBuilderPositionAverage(ReportBuilderBase):
    """Per position analysis builder.

    Parameters
    ----------

    outputRoot: str, optional
        Path to the directory where all reports should be put

        (Default: ``None``)

    outputNamePrefix: str, optional
        Partial name to be added to all reports done by the builder

        (Default: ``None``)

    undecidedValue: int, optional
        The value for which undecided items were encoded (so it
        can be omited and calculated separately for 2 of 3 graphs).

        (Default: 0.5)

    *reports: objects, optional
        Any number of reports to be added from start

        (Default: fseq.LinePlot) 

    Attributes
    ----------

    undecidedValue

    See also
    --------

    ReportBuilderBase
        Base class which implements some more attributes.
    """

    DEFAULT_REPORTS = (fseq.LinePlot, )

    def __init__(self, *reports, **kwargs):
        """
        Parameters
        ----------

        outputRoot: str, optional
            Path to the directory where all reports should be put

            (Default: ``None``)

        outputNamePrefix: str, optional
            Partial name to be added to all reports done by the builder

            (Default: ``None``)

        undecidedValue: int, optional
            The value for which undecided items were encoded (so it
            can be omited and calculated separately for 2 of 3 graphs).

            (Default: 0.5)

        *reports: objects, optional
            Any number of reports to be added from start

            (Default: fseq.LinePlot) 
        """

        if len(reports) == 0:
            reports = tuple(r() for r in self.DEFAULT_REPORTS)

        super(ReportBuilderPositionAverage, self).__init__(*reports, **kwargs)

        self.undecidedValue = 'undecidedValue' in kwargs and \
            kwargs['undecidedValue'] or 0.5

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
            Any args will be passed to the ``ReportBuilderBase.distill``

        **kwargs:
            Any kwargs will be passed to the ``ReportBuilderBase.distill``

            **Note:** ``outputNamePrefix`` will be overwritten/added

        Returns
        -------

        fseq.ReportBuilderPositionAverage
            Returns ``self``
        """
        
        if undecidedValue is None:
            undecidedValue = self.undecidedValue

        super(ReportBuilderPositionAverage, self).distill(
            data.mean(axis=0, dtype=np.float),
            outputNamePrefix='average.total.',
            title='Average GC per position',
            xlabel='Read position',
            ylabel='%GC',
            *args, **kwargs)

        freqs, bins = zip(*(self._floatBin(C) for C in data.T))
        undecidedV = np.ones_like(freqs) * undecidedValue

        lacking = np.frompyfunc(self._getF, 3, 1)

        super(ReportBuilderPositionAverage, self).distill(
            lacking(freqs, bins, undecidedV),
            title='Frequency of missing data per position',
            xlabel='Read position',
            ylabel='f',
            outputNamePrefix='average.lacking.', *args, **kwargs)
    
        notLacking = np.frompyfunc(self._getNotF, 3, 1)

        super(ReportBuilderPositionAverage, self).distill(
            notLacking(freqs, bins, undecidedV),
            title='Average GC per position, omitting uncertain',
            xlabel='Read position',
            ylabel='%GC',
            outputNamePrefix='average.not-lacking.', *args, **kwargs)

        return self

