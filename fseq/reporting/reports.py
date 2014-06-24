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

    Parameters 
    ----------

    name: str, optional
        A specific name of the report

        (Default: ``None``)

    saveArgs: tuple or list, optional
        Any args to be passed to ``matplotlib.savefig`` after the figure

        (Default: Empty ``tuple``)

    saveKwargs: dict, optional
        Any keyword args to be passed to ``matplotlib.savefig``

        (Default: Empty ``dict``)

    Attributes
    ----------

    name
    saveArgs
    saveKwargs
    """

    def __init__(self, name=None, saveArgs=tuple(), saveKwargs=dict()):
        """
        Parameters
        ----------

        name: str, optional
            A specific name of the report

            (Default: ``None``)

        saveArgs: tuple or list, optional
            Any args to be passed to ``matplotlib.savefig`` after the figure

            (Default: Empty ``tuple``)

        saveKwargs: dict, optional
            Any keyword args to be passed to ``matplotlib.savefig``

            (Default: Empty ``dict``)
        """

        self.name = name
        self.saveArgs = saveArgs
        self.saveKwargs = saveKwargs

    @property
    def name(self):
        """Name of the plot, used to name the file: str"""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def saveArgs(self):
        """Save args passed to ``matplotlib.pyplot.figure.savefig``: tuple"""
        return self._saveArgs

    @saveArgs.setter
    def saveArgs(self, args):

        self._saveArgs = args

    @property
    def saveKwargs(self):
        """Save keyword args passed to ``matplotlib.pyplot.figure.savefig``:
        dict
        """

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

            (Default: Use the ``self.name`` of the instance)

            **Note:** If none supplied and none set for instance,
            ``ValueError`` is raised.

        *args:
            Any arguments to be sent to ``matplotlib.Figure.save``.
            If none added the ``ReportBase.saveArgs`` will be used.

        **kwargs:
            Any keyword arguments to be sent to ``matplotlib.Figure.save``.
            If notn addd the ``ReportBase.saveKwargs`` will be used.

        Returns
        -------

        ReportBase
            Returns ``self``

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

        print("Saving -> {0}".format(path))

        fig.savefig(path, *args, **kwargs)

        return self

    def distill(self, data, outputRoot=None, outputNamePrefix=None,
            *args, **kwargs):
        """Placeholder distill interface not to be used.

        Raises
        ------

        NotImplementedError
            Always raises this exception
        """

        raise NotImplementedError("This method should be overwritten")


class HeatMap(ReportBase):
    """Makes heatmaps from data

    Parameters
    ----------

    name: str, optional
        A specific name of the report

        (Default: "heatmap.pdf")

    saveArgs: tuple or list, optional
        Any args to be passed to ``matplotlib.savefig`` after the figure

        (Default: Empty tuple)

    saveKwargs: dict, optional
        Any keyword args to be passed to ``matplotlib.savefig``

        (Default: Empty dict)
    """

    def __init__(self, name='heatmap.pdf', saveArgs=tuple(), saveKwargs=dict()):
        """
        Parameters
        ----------

        name: str, optional
            A specific name of the report

            (Default: "heatmap.pdf")

        saveArgs: tuple or list, optional
            Any args to be passed to ``matplotlib.savefig`` after the figure

            (Default: Empty tuple)

        saveKwargs: dict, optional
            Any keyword args to be passed to ``matplotlib.savefig``

            (Default: Empty dict)
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

            (Default: Use the value of ``self.name``)

        outputRoot: str, optional
            The directory in which to place the report

            (Default: ``None``)

        outputNamePrefix: str, optional
            A prefix to prepend the name when saving the output.
            Typically set by the builder to indicate what post-processing
            was done to the data shown in the report.

            (Default: ``None``)

        title: str, optional
            A title to be put over the heatmap
            (Default: ``None``, value automatically scaled by matplotlib)

            (Default: ``None``)

        text: str, optional
            An explanatory text to put under the plot

            (Default: ``None``)

            **Note:** This feature has not been implemented yet.

        ylabel: str, optional
            A label for the y-axis

            (Default: ``None``)

        xlabel: str, optional
            A label for the x-axis

            (Default: ``None``)

        saveArgs: tuple or list, optional
            A set of arguments to overwrite the instance's default save args

            (Default: empty tuple)

        saveKwargs: dict, optional
            A set of keyword arguments to overwrite the instanc's default

            (Default: empty dict)

        vmin: number, optional
            To set a minimum color-scale number for the heatmap

            (Default: ``None``, value automatically scaled by matplotlib)

        vmax: number, optional
            To set a maximum color-scale number for the heatmap

            (Default: ``None``, value automatically scaled by matplotlib)

        aspect: str, optional
            The aspect ratio of the blocks/pixels in the heatmap
            
            (Default: 'auto', which allows for rectangular pixels)

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
    """Makes lines from data

    Parameters
    ----------

    name: str, optional
        A specific name of the report

        (Default: "line.pdf")

    saveArgs: tuple or list, optional
        Any args to be passed to ``matplotlib.savefig`` after the figure

        (Default: Empty tuple)

    saveKwargs: dict, optional
        Any keyword args to be passed to ``matplotlib.savefig``

        (Default: Empty dict)
    """

    def __init__(self, name="line.pdf", saveArgs=tuple(), saveKwargs=dict()):
        """
        Parameters
        ----------

        name: str, optional
            A specific name of the report

            (Default: "line.pdf")

        saveArgs: tuple or list, optional
            Any args to be passed to ``matplotlib.savefig`` after the figure

            (Default: Empty tuple)

        saveKwargs: dict, optional
            Any keyword args to be passed to ``matplotlib.savefig``

            (Default: Empty dict)
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

            (Default: Use the value of ``self.name``)

        outputRoot: str, optional
            The directory in which to place the report

            (Default: ``None``)

        outputNamePrefix: str, optional
            A prefix to prepend the name when saving the output.
            Typically set by the builder to indicate what post-processing
            was done to the data shown in the report.

            (Default: ``None``)

        title: str, optional
            A title to be put over the heatmap
            (Default: ``None``, value automatically scaled by matplotlib)

            (Default: ``None``)

        text: str, optional
            An explanatory text to put under the plot

            (Default: ``None``)

            **Note:** This feature has not been implemented yet.

        ylabel: str, optional
            A label for the y-axis

            (Default: ``None``)

        xlabel: str, optional
            A label for the x-axis

            (Default: ``None``)

        saveArgs: tuple or list, optional
            A set of arguments to overwrite the instance's default save args

            (Default: empty ``tuple``)

        saveKwargs: dict, optional
            A set of keyword arguments to overwrite the instanc's default

            (Default: empty ``dict``)

        logX: bool, optional
            If X-axis should be logged

            (Default: ``False``)

        logY: bool, optional
            If Y-axis should be logged

            (Default: ``False``)

        basex: number, optional
            To specify other then 10-base logging

            (Default: ``None``, uses 10-base)

        basey: number, optional
            To specify other than 10-base logging

            (Default: ``None``, uses 10-base)

        labels: str, optional
            To name the line plotted and thus add a legend to the plot.

            (Default: ``None``)
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
            ax.legend(prop={'size': 'x-small'})

        if title is not None:
            ax.set_title(title)
        if text is not None:
            pass
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        if xlabel is not None:
            ax.set_xlabel(xlabel)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.get_xaxis().tick_bottom()
        ax.get_yaxis().tick_right()

        f.tight_layout()

        self.saveFig(f, outputRoot=outputRoot,
                outputNamePrefix=outputNamePrefix,
                name=name, *saveArgs, **saveKwargs)
