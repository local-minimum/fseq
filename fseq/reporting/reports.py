#!/usr/bin/env python
"""Module for holding the various implemented reporting classes"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import warnings


class ReportBase(object):
    """Base class for simple report creations.

    Main purpose is to make a common interface for figure saving using
    matplotlib figures.

    Attributes
    ----------

    name
    saveArgs
    saveKwargs
    """

    def __init__(self, name=None, saveArgs=tuple(), saveKwargs=dict()):
        """
        Properties
        ----------

        name: str, optional
            A specific name of the report

        saveArgs: tuple or list, optional
            Any args to be passed to `matplotlib.savefig` after the figure

        saveKwargs: dict, optional
            Any keyword args to be passed to `matplotlib.savefig`
        """

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


class HeatMap(ReportBase):
    """Makes heatmaps from data"""

    def __init__(self, name='heatmap.pdf', saveArgs=tuple(), saveKwargs=dict()):
        """
        Properties
        ----------

        name: str, optional
            A specific name of the report
            (Default: 'heatmap.pdf')

        saveArgs: tuple or list, optional
            Any args to be passed to `matplotlib.savefig` after the figure

        saveKwargs: dict, optional
            Any keyword args to be passed to `matplotlib.savefig`
        """

        super(HeatMap, self).__init__(name=name, saveArgs=saveArgs,
            saveKwargs=saveKwargs)

    def distill(self, data, name=None, outputRoot=None, outputNamePrefix=None,
            title=None, text=None, ylabel=None, xlabel=None,
            saveArgs=tuple(), saveKwargs=dict(), vmin=None, vmax=None,
            aspect='auto', axisOff=True,
            cmap=plt.cm.RdBu, *args, **kwargs):
        """Creates the actual heatmap.

        Parameters
        ----------

        data: numpy.ndarray
            The data to be plotted

        name: str, optional
            If the default name of the HeatMap instance should be overwritten

        outputRoot: str, optional
            The directory in which to place the report

        outputNamePrefix: str, optional
            A prefix to prepend the name when saving the output.

        title: str, optional
            A title to be put over the heatmap

        text: str, optional
            An explanatory text to put under the plot

        ylabel: str, optional
            A label for the y-axis

        xlabel: str, optional
            A label for the x-axis

        saveArgs: tuple or list, optional
            A set of arguments to overwrite the instance's default save args

        saveKwargs: dict, optional
            A set of keyword arguments to overwrite the instanc's default

        vmin: number, optional
            To set a minimum color-scale number for the heatmap

        vmax: number, optional
            To set a maximum color-scale number for the heatmap

        aspect: str, optional
            The aspect ratio of the blocks/pixels in the heatmap, default
            is 'auto', which allows for rectangular pixels.

        axisOff: bool, optional
            If the axis of the plot should not be rendered
            (Default: True)
            
        cmap: matplotlib.cmap, optional
            A colormap to be used when plotting.
            (Default: Red -- Blue)
        """

        if len(args):
            warnings.warn("Unused arguments: {0}".format(args))
        if len(kwargs):
            warnings.warn("Unused keyword arguments: {0}".format(kwargs))

        f = plt.figure(name)
        ax = f.gca()
        im = ax.imshow(data, aspect=aspect, cmap=cmap, interpolation='nearest',
                       vmin=vmin, vmax=vmax)

        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

        plt.colorbar(im, ax=ax)

        if axisOff:
            ax.axis('off')

        if title is not None:
            ax.set_title(title)

        f.tight_layout()

        self.saveFig(f, outputRoot=outputRoot,
                outputNamePrefix=outputNamePrefix,
                name=name, *saveArgs, **saveKwargs)


class LinePlot(ReportBase):
    """Makes lines from data"""

    def __init__(self, name="line.pdf", saveArgs=tuple(), saveKwargs=dict()):
        """
        Properties
        ----------

        name: str, optional
            A specific name of the report

        saveArgs: tuple or list, optional
            Any args to be passed to `matplotlib.savefig` after the figure

        saveKwargs: dict, optional
            Any keyword args to be passed to `matplotlib.savefig`
        """

        super(LinePlot, self).__init__(name=name, saveArgs=saveArgs,
            saveKwargs=saveKwargs)

    def distill(self, data, name=None, outputRoot=None, outputNamePrefix=None,
            title=None, text=None, ylabel=None, xlabel=None,
            saveArgs=tuple(), saveKwargs=dict(), logX=False, logY=False,
            basex=None, basey=None, labels=None,
            *args, **kwargs):

        """Creates the actual heatmap.

        Parameters
        ----------

        data: numpy.ndarray
            The data to be plotted

        name: str, optional
            If the default name of the HeatMap instance should be overwritten

        outputRoot: str, optional
            The directory in which to place the report

        outputNamePrefix: str, optional
            A prefix to prepend the name when saving the output.

        title: str, optional
            A title to be put over the heatmap

        text: str, optional
            An explanatory text to put under the plot

        ylabel: str, optional
            A label for the y-axis

        xlabel: str, optional
            A label for the x-axis

        saveArgs: tuple or list, optional
            A set of arguments to overwrite the instance's default save args

        saveKwargs: dict, optional
            A set of keyword arguments to overwrite the instanc's default
        
        logX: bool, optional
            If X-axis should be logged

        logY: bool, optional
            If Y-axis should be logged

        basex: number, optional
            To specify other then 10-base logging

        basey: number, optional
            To specify other than 10-base logging

        labels: str, optional
            To name the line plotted and thus add a legend to the plot.
        """
        if len(args):
            warnings.warn("Unused arguments: {0}".format(args))
        if len(kwargs):
            warnings.warn("Unused keyword arguments: {0}".format(kwargs))

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

        f.tight_layout()

        self.saveFig(f, outputRoot=outputRoot,
                outputNamePrefix=outputNamePrefix,
                name=name, *saveArgs, **saveKwargs)
