#!/usr/bin/env python
"""Module for reading sequence data"""

import os
import numpy as np

import fseq



class SeqReader(object):
    """Reads sequence data and encodes it.

    The length of the sequence reader reflects the number of inputs to be
    processed.

    The entire stack of inputs can be processed in bulk by invoking
    `SeqReader.run()` but the results of each encoding, omitting any
    report building can also be produced iteratively as shown in the examples.

    Attributes
    ----------
    popDataSources
    popEncodingResults
    jobQueue
    reportBuilders
    reportDirectory
    SeqEncoder
    resetSeqEncoder
    results

    Examples
    --------

    To invoke the reader it can either be run :
    >>> seqReader.run()
    <fseq.reading.seq_reader.SeqReader at 0x7faf6970fd10>

    or if more control is required, it can be iterated over:
    >>> for res in seqReader:
    ...    reportBuilder.distill(res, dirname=seqReader.reportDirectory)

    Both methods above yielding the same result with the difference that
    the first may store results in `seqReader.results` depending on the
    `seqReader.popEncodingResults` settings while the latter never keeps
    the results in the state of the instance.
    """

    def __init__(
            self, seqEncoder=None, dataSourcePaths=None, dataTargetPaths=None,
            reportBuilder=None, popDataSources=True, resetSeqEncoder=True,
            popEncodingResults=None):
        """
        Parameters
        ----------

        seqEncoder : fseq.SeqEncoder, optional
            An instance of a sequence encoder that will be used to encode the
            input strings
            (Default: No specified encoder) 

        dataSourcePaths: string or iterable object, optional
            Either a path string or a collection of paths to data files
            (Default: no input / added later)

        dataTargetPaths: string or iterable object, optional
            Either a relative path string or collection of relative paths.
            The path is relative to the respective data source.
            (Default: will create a folder in the same directory as the 
            data source with the same name as the input suffixed by `.reports`.)
            ..note:: If supplied, must reflect equal number of outputs as
                inputs in `dataSourcePaths` 

        reportBuilder: fseq.ReportBuilder, optional
            If a report should be automatically be built upon encoding
            completion.
            (Default: no report builder)

        popDataSources: bool, optional
            If data sources should be removed from stack once encoded
            (Default: `True`)

        resetSeqEncoder: bool, optional
            If sequence encoder should be reset between each source file or
            if the encoder should expect all sources to be the same format.
            (Default: `True`)

        popEncodingResults: bool, optional
            If encoding results should be popped after they have been processed.
            (Default: `True` is more than one source, else `False`)
        """

        self._idData = -1
        self._reportBuilders = []
        self._dataSourcePaths = []
        self._dataTargetPaths = {}
        self._seqEncoder = None
        self._reportTargetBase = ""
        self._results = []

        if seqEncoder:
            self.seqEncoder = seqEncoder

        if dataSourcePaths:
            self.addData(dataSourcePaths, targetPaths=dataTargetPaths)

        if reportBuilder:
            self.addReportBuilder(reportBuilder)

        self.popDataSources = popDataSources
        self.resetSeqEncoder = resetSeqEncoder
        self._seqEncoder = None

        if popEncodingResults is None:
            self.popEncodingResults = len(self) > 1
        else:
            self.popEncodingResults = popEncodingResults
    
    def __iter__(self):

        self._idData = 0
        return self

    def __len__(self):

        return len(self._dataTargetPaths)

    @property
    def popDataSources(self):
        """If sequence reader should remove data sources from list of sources
        when they have been read.

        The general use case is to set this to `True`, but omitting popping
        can be useful if data may be needed to be re-read with a different
        encoder.
        
        Returns
        -------
        
        bool
        """
        return self._popDataSources

    @popDataSources.setter
    def popDataSources(self, val):

        self._popDataSources = bool(val)
        if (self._popDataSources):
            self._idData = -1

    @property
    def popEncodingResults(self):
        """If the outcome of an encoding should be remove from memory as soon
        as report as been produced or iteration completed.

        ..note:: The process will require large amounts of memory if results
        are not popped and several large files analysed.

        Returns
        -------

        bool
        """
        return self._popEncodingResults

    @property
    def jobQueue(self):
        """The data sources to be read and their respective targets.

        Returns
        -------

        list of tuples
            Each tuple representing a source - target pair.
        """
        return zip(self._dataSourcePaths, self._dataTargetPaths)

    @property
    def results(self):
        """A list of the results of the encodings.
        
        Returns
        -------
        
        list
        
        See also
        --------
        
        seqEncoder.clearResults
            Clearing the list of results
        """

        return self._results

    @popEncodingResults.setter
    def popEncodingResults(self, val):

        self._popEncodingResults = bool(val)

    @property
    def seqEncoder(self):
        """The encoder attached to the sequence reader that will parse the
        input strings into values.

        Returns
        -------

        fseq.SeqEncoder
            Current encoder

        Raises
        ------

        TypeError
            If trying to assign object that is not a `fseq.SeqEncoder`
        
        """

        return self._seqEncoder

    @seqEncoder.setter
    def seqEncoder(self, encoder):

        if not isinstance(encoder, fseq.SeqEncoder):

            raise TypeError(
                "Encoder {0} is not a `fseq.SeqEncoder`".format(encoder))
        else:

            self._seqEncoder = encoder

    @property
    def resetSeqEncoder(self):
        """If each data source will detect format anew or if all files are
        assumed to be of the same format
        
        Returns
        -------
        
        bool
        """

        return self._resetSeqEncoder

    @resetSeqEncoder.setter
    def resetSeqEncoder(self, val):

        self._resetSeqEncoder = bool(val)

    @property
    def reportBuilders(self):
        """The report builders associated with the reader.

        If any, the reports will be destilled automatically at the end of
        `SeqReader.run()`.

        Returns
        -------

        tuple
            The currently assigned report builders

        See also
        --------

        fseq.ReportBuilder.distill
            Method for distilling encoded data.
        """

        return (r for r in self._reportBuilders)

    @property
    def reportDirectory(self):
        """The directory where reports for the last made encoding should go.

        Returns
        -------

        str
        """
        return self._reportTargetBase

    def addData(self, sourcePaths, targetPaths=None):
        """Add a data source path to be analysed.

        Parameters
        ----------

        sourcePaths: string or iterable object
            Either a path string or a collection of paths to data files

        targetPaths: string or iterable object, optional
            Either a relative path string or collection of relative paths.
            The path is relative to the respective data source.
            (Default: will create a folder in the same directory as the 
            data source with the same name as the input suffixed by `.reports`.)
            ..note:: If supplied, must reflect equal number of outputs as
                inputs in `sourcePaths` 

        Returns
        -------

        fset.SeqReader
            Returns `self`

        Raises
        ------

        ValueError
            If target paths are supplied but don't match in lenght with the
            number of source-paths
        """

        if isinstance(sourcePaths, str):
            sourcePaths = (sourcePaths, )
        if isinstance(targetPaths, str):
            targetPaths = (targetPaths, )

        if targetPaths is not None and len(sourcePaths) != len(targetPaths):
            raise ValueError(
                "Un-equal number of sources ({0}) and targets ({1})".format(
                    len(sourcePaths), len(targetPaths)))

        if targetPaths is None:

            targetPaths = [os.path.basename(s) + ".reports"
                           for r in sourcePaths]

        self._dataSourcePaths += list(sourcePaths)
        self._dataTargetPaths += list(targetPaths)

        return self

    def addReportBuilder(self, reportBuilder):
        """Add a report builder to the set of reports done upon analysis.

        Parameters
        ----------

        reportBuilder: fseq.ReportBuilder
            Report builder to be added

        Returns
        -------

        fset.SeqReader
            Returns `self`

        Raises
        ------

        TypeError
            If `reportBuilder` is not a valid `fseq.ReportBuilder`
        """

        if not isinstance(reportBuilder, fseq.ReportBuilder):

            raise TypeError(
                "Report Builder {0} is not a `fseq.ReportBuilder`".format(
                    ReportBuilder))

        else:

            self._reportBuilders.append(reportBuilder)

        return self

    def clearJobQueue(self):
        """Removes all jobs in the queue.

        Returns
        -------

        fset.SeqReader
            Returns `self`
        """

        self._dataSourcePaths = []
        self._dataTargetPaths = []

        return self

    def clearResults(self):
        """Removes all stored results of encodings

        Returns
        -------

        fset.SeqReader
            Returns `self`
        """

        self._results = []

        return self

    def removeReportBuilders(self, *builders):
        """Removes all builders supplied, or all builders if no specific
        builder is supplied.

        Parameters
        ----------

        *args: fseq.ReportBuilder, optional
            Any number of report builder references for report builders to
            be removed.
            If none is supplied, all report builders will be removed.

        Returns
        -------

        fset.SeqReader
            Returns `self`

        Examples
        --------

        If current instance has three builders:
        >>> tuple(seqEncoder.reportBuilders)
        (b1, b2, b3)

        The `b2` and `b3` can be removed by:
        >>> seqEncoder.removeReportBuilders(b2, b3)
        <fseq.reading.seq_reader.SeqReader at 0x7faf696e5810>

        >>> tuple(seqEncoder.reportBuilders)
        (b1, )

        Alternatively all builders can be removed by:
        >>> seqEncoder.removeReportBuilders()
        <fseq.reading.seq_reader.SeqReader at 0x7faf696e5810>

        >>> tuple(seqEncoder.reportBuilders)
        ()
        """

        self._reportBuilders = [b for b in self._reportBuilders if b not in
                                builders and len(builders) > 0]
        
        return self

    def run(self):
        """Runs through all sources and produces reports if such have been
        attached.

        Returns
        -------

        fset.SeqReader
            Returns `self`
        """

        for res in self:

            for rb in self._reportBuilders:

                rb.distill(res, dirname=self.reportDirectory)

            if not self.popEncodingResults:

                self._results.append(rb)

        return self

    def next(self):
        """Part of iter interface, produces the encoding of the next
        data-source.

        Returns
        -------

        numpy.ndarray
            Encoding output.

        Raises
        ------

        ValueError
            If no encoder has been assigned.

        StopIteration
            If no more data-source exists.
        """

        E = self.SeqEncoder

        if E is None:
            raise ValueError("No encoder present")

        if len(self) == 0 or self._idData == len(self):
            raise StopIteration()

        if self.popDataSources:
            source = self._dataSourcePaths.pop(0)
            self._reportTargetBase = os.path.join(
                os.path.dirname(source), self._dataTargetPaths.pop(0))
        else:
            source = self._dataSourcePaths[self._idData]
            self._reportTargetBase = os.path.join(
                os.path.dirname(source), self._dataTargetPaths[self._idData])
            self._idData += 1

        if self.resetSeqEncoder:
            E.reset()

        D = np.array()
        

        raise NotImplemented()

        return D