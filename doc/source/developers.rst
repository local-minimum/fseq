Developers
==========

``fseq`` has been written to initially take care of a very limited set of
analysis and sequence formats, while at the same time be written to be
highly extensible.

Some examples of suitable features to be included in the future:

    - **FastQ SeqFormat Subclasses**

      Sub-classing ``fseq.FastQ`` to automatically detect which quality encoding
      was used based on the range of values in the quality lines fed to the
      ``SeqFormat``.

    - **SeqEncoderQaulity SeqEncoder Subclass**

      A subclass that encodes the quality line using the quality encoding
      supplied by the ``SeqFormat`` detected.

Git
---

The source code project is hosted at:

https://gitorious.org/fseq

For merge requests, the code is expected to:

    - Be documented in accordance with ``numpydoc``-format
      (see https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt)

    - Code to be PEP8 compliant
      (see http://legacy.python.org/dev/peps/pep-0008/)

    - Coding style in general to follow the style established in `fseq`

    - Git commits to in general be *informative* and have
      *one aspect changed per commit*

Reading
-------

To extend the functionality by adding further encoders, these encoders should
be derived from ``fseq.SeqEncoder`` and as a minimal requirement need to
overwrite the ``fseq.SeqEncoder.parse``-method.

To extend the functionality by adding support for more input formats, classes
should be derived from ``fseq.SeqFormat`` or any of the already implemented
formats if they partially solve detection for the new format.
Minimal requirement is overwriting the ``fseq.SeqFormat.expects``-method, but
typically many of the properties of the base class as well as the
constructor needs replacing.

``fseq.SeqEncoder.parse(self, lines, out, outindex)`` overwriting
.................................................................

**Important 1:** The overwritten ``fseq.SeqEncoder.parse`` must have identical
parameter set. If further information is needed, this should be dealt with
during initiation or by separate methods.

**Important 2:** The overwritten method may not throw any errors and should silently
handle scenarios where the length of the information to be encoded mismatches
the length of the corresponding slot of the ``out`` object.

Example of how out the second important note can be achieved (adapted from
``fseq.SeqEncoderGC.parse``)::

    #Point to line of interes
    l = lines[self._sequence_line]

    #Put the contents of that line directly into out
    out[outindex][:len(l)] = l[:out.shape(1)]

The above example is quite useless as an encoder as it doesn't translate
the contents of the input in any way, but the ``[:len(l)]`` on ``out`` 
ensures the target slot of ``out`` is not too large, while the
``[:out.shape(1)]`` ensures that `l` is not too large for the slot in ``out``.

**Important 3:** The ``parse``-method may use the state of the class instance
(as in the above example), but due to concurrency issues, *it should not alter
the state*.


``fseq.SeqFormat`` sub-classing
...............................

** Important 1:** If a class is parent to further sub-classing such that the
class will conform to all data that the more specific subclass will do
(e.g. FastQ will be expect all lines/return ``True`` for all scenarios that
a FastQ_Q33-subclass that detects fastq-files with encoding starting at 33),
then:

    - The *parent* should implement the ``fseq.SeqFormat._decay`` method similar
      to the base class and have a suitable ``self._giveup`` set in its init.

    - The specific *child* should overwrite the ``_decay``-method so that it
      never gives up *or alternatively* takes longer before it gives up by
      having ha higher number set to ``self._giveup`` in init.

The ``self.expect(line)`` should return a boolean if the line fits what was
expected as the next line, this method doesn't need to continue 
reporting ``False`` after its first occurrence.
As soon as an ``expect``-method returns a ``False``, that ``SeqFormat`` is
removed from possible formats by the ``SeqFormatDetector``.

Reporting
---------

To extend the available abstractions/analysis done to the encoded
data, new derived ``ReportBuilderBase`` classes should be made.
Typically the ``__init__`` and ``distill`` would be overwritten (but the super
class methods called), and the ``DEFAULT_REPORTS`` attribute replaced.
Potentially the interface extended by more relevant methods and properties
needed for user customization of the post-processing.

For creating new reports any object having a ``distill``-method will do, but
using ``fseq.ReportBase`` will save some implementation by having implemented
the common aspects of saving figures in ``matplotlib``.

``fseq.ReportBuilderBase`` sub-classing
.......................................

To maintain the constructor interface it is highly recommended that the init
has the following structure::

    def __init__(self, *reports, **kwargs):

        if len(reports) == 0:
            reports = tuple(r() for r in self.DEFAULT_REPORTS)

        super(MyReportBuilder, self).__init__(*reports, **kwargs)

        #Emulating default values for keywords is done by getting
        #the key with default values as follows
        self.someKey = kwargs.get('someKey', defaultValue)

To push some data to all attached reports make a ``super`` call to
``ReportBuilderBase.distill``.

``fseq.ReportBase`` sub-classing or not
.......................................

Using ``ReportBase`` to create new reports is entirely optional, but if the
report is a ``matplotlib``-report, then it is probably useful.

If sub-classing, then the ``ReportBase.distill`` must be overwritten and
subclass should use a call to the inherited ``saveFig``-method to do the
actually saving once the figure has been setup within the ``distill`` method.

If using other modules than ``matplotlib`` and thereby not sub-classing
``ReportBase``, the report should as a minimal requirement have a
``distill`` method that takes the main data as the first argument and that
accepts any number of argument and keyword arguments by having something like
``*args, **kwargs`` at the end of the parameter list.
