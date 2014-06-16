#!/usr/bin/env python
"""Module for holding the various implemented reporting classes"""

import matplotlib.pyplot as plt
import os


class ReportBase(object):

    def __init__(self, name=None, saveArgs=tuple(), saveKwargs=dict()):

        self.name = name
        self.saveArgs = saveArgs
        self.saveKwargs = saveKwargs

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def saveArgs(self):

        return self._saveArgs

    @saveArgs.setter
    def saveArgs(self, args):

        self._saveArgs = args

    @property
    def saveKwargs(self):

        return self._saveKwargs

    @saveKwargs.setter
    def saveKwargs(self, kwargs):

        self._saveKwargs = kwargs

    def saveFig(self, fig, outputRoot, outputNamePrefix, name=None,
            *args, **kwargs):
        """Saves a figure and creates directories if needed.
        
        Parameters
        ----------

        fig: matplotlib.figure
            The figure to be saved

        outputRoot: str
            The root directory for reports

        outputNamePrefix: str
            If the name of the file should be prepended by some string.
            Normally added by the *Report Builder*

        name: str, optional
            A specific name for this figure-file.
            If none supplied the default name for the report will be used,
            if no such has been set `ValueError` is raised.

        *args:
            Any arguments to be sent to `matplotlib.Figure.save`.
            If none added the `ReportBase.saveArgs` will be used.

        **kwargs:
            Any keyword arguments to be sent to `matplotlib.Figure.save`.
            If notn addd the `ReportBase.saveKwargs` will be used.

        Returns
        -------

        ReportBase
            Returns `self`

        Raises
        ------

        ValueError
            If no name has been given.
        """

        if name is None:
            name = self._name
            if name is None:
                raise ValueError("Can't save file when no name give to report")

        path = os.path.join(outputRoot, outputNamePrefix + name)

        try:
            os.makedirs(os.path.dirname(path))
        except OSError:
            pass

        if len(args) == 0:
            args = self.saveArgs

        if len(kwargs) == 0:
            kwargs = self.saveKwargs

        fig.savefig(path, *args, **kwargs)

        return self

    def distill(self, data, outputRoot=None, outputNamePrefix=None,
            *args, **kwargs):
        """Placeholder distill interface not to be used.

        Raises
        ------

        NotImplemented
            Always raises this exception
        """

        raise NotImplemented("This method should be overwritten")


class LinePlot(ReportBase):

    def __init__(self, name="line.pdf", saveArgs=tuple(), saveKwargs=dict()):

        super(LinePlot, self).__init__(name=name, saveArgs=saveArgs,
            saveKwargs=saveKwargs)

    def distill(self, data, name=None, outputRoot=None, outputNamePrefix=None,
            title=None, text=None, ylabel=None, xlabel=None,
            saveArgs=tuple(), saveKwargs=dict(), logX=False, logY=False,
            basex=None, basey=None, labels=None,
            *args, **kwargs):

        f = plt.figure(name)
        ax = f.gca()
        if logX and logY:
            ax.loglog(data, '-g', lw=2, basey=basey, basex=basex, label=labels)
        elif logX:
            ax.semilogx(data, '-g', lw=2, basex=basex, label=labels)
        elif logY:
            ax.semilogy(data, '-g', lw=2, basey=basey, label=labels)
        else:
            ax.plot(data, '-g', lw=2)

        if labels:
            ax.legend()

        if title is not None:
            ax.set_title(title)
        if text is not None:
            pass
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

        self.saveFig(f, outputRoot=outputRoot,
                outputNamePrefix=outputNamePrefix,
                name=name, *saveArgs, **saveKwargs)
