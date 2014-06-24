fSeq Project Report for C3SE Graduate Course: Python and High Performance Computing 2014
========================================================================================

Abstract
--------

*fSeq* was created for the C3SE Graduate Course [c3se]_, in part for want of
suitable existing project or code base.
Therefor only part of the course content
could be covered -- ``numpy``, ``scipy``, ``matplotlib``, ``unittest`` and
``sphinx`` being the most prominent.
It is a versitile and efficient tool to build future sequence analyses into.
The package contains classes to do simple per base analysis of the data as is
existing elsewere in e.g. [fastqc]_.
However, it also extends sequence quality analysis with heatmaps of 
clustered fourier data, which to the best of my knownledge, is novel to the
field.
These reflect previously identified issues of sequence data but also introduces
new frequency features, which requires further investigation.


Solution Method
---------------

Design Analysis
...............

The task was split up into several well defined components:

- **Reading data**

  This feature can be held generic, it will need to be able to talk to
  both encoders and format detectors on one side as well as post-processing
  classes on the other.

  The class can do several parts in parallell:

    - Reading data from file

    - Encoding chunks of data

    - Reporting on encoded data

- **Detecting input data format**

  To be able to support several formats and allow for future extension of
  formats supported, the task should be separated into `selecting suitable
  detector` among a collection of format collectors and `detecting particular
  formats`. 

  The latter should have a common interface for the former to use, thus a
  base class that the detectors can subclass is suitable.

  The logic of the formats differ enough that making a factory design pattern
  would probably require more than is gained.

- **Encoding input**

  Potentially there is an unknown number of ways to encode the data.

  The data reader needs an interface where objects can be sent such that
  no concurrency issues can arise, that is, it may not alter the state.
  This interface needs to be common to all encoders.

  To simplify the use, the encoder can manage its format detector

  The encoder can suggest default post-processors to be coupled with it in
  the reader.
  This will make the invocation less transparent, but greatly reduce the
  workload of the user.
  Thus the user must be able to override the default coupling, and this
  manner must be clear.

- **Post-processing encoded input**

  One type of encoding can potentially be used for several downstream analyses.
  However, it is not inherently clear if some aspects should be done by the
  encoder directly or the post-processing class.

  The post-processing class should coordinate all outputs made from its data.

  It should assist in naming and annotation to clarify the contents of the
  report.

  Reports from one post-processor should be grouped by file name.

  Post-processors need to have a common interface that doesn't alter the state
  for the reader to use.

- **Producing outputs**

  Dependence on graphics libraries such as ``matplotlib`` should be restricted
  to the output generators.

  These classes also need to have a common interface for the post-processors
  and may not alter the state (due to concurrencies).

  An output producer should be reusable for several post-processors.

General
^^^^^^^

The default invokation of analysis should require a minimum of user input.
For each deviation for what is considered *default*, a new set of default
behaviours should exist.

The interdependence of the classes should be kept simple and clean such that 
each class can be instatiated and as a maximum be needed as a parameter to
one other class.

The complete setup and configuration of a class should be possible via its
constructor and methods returning ``self`` such that all imaginable
combinations of settings can be setup and run in a single line.

Parallellism
............

As described above, the main target for explicit coding of parallell computing
is the reader object.

To be able to easily share the data storing ``numpy.ndarray``, ``treading`` was
selected. Other considered modules were ``multiprocessing`` and ``pycuda``,
however due to limitations in implementation time the former was used.

Still parallellism poses several issues, the size of the array cannot be
changed without creating a new object, while the needed size cannot be known
before the contents of the file has been read.
If the whole file is scanned, reading is impossible due to the large amount of
memory needed, a large benefit of threading would have been lost.

Therefore, a design was opted for where the main thread creates a large array
and several threads are used to fill that array up from data read from the
source file.
When the array is full, the main thread must pause, reading data and wait for
all live theads to finnish, after which the array can be extended. 
Then, reading and threading can start again.

Unittesting
...........

Test driven development [tdd]_ was considered, but as development and 
especially design time was exteremely limited, testing was decided to:

- Verify all isolated behaviours

- Verify all interdependent behaviours that don't require running the
  entire analysis nor would produce files on the hard drive.

The tests were decided to be placed inside the package but not be part
of the distribution.

Documentation
.............

The documentation of the code should be compatible with ``sphinx`` [sphinx]_
and follow the ``numpydoc`` [npd]_ standard of restructured text [rst]_.

Implementation
--------------

Package structure
.................

The relevant folder tree for the package was devised as follows:

- fseq (root of *git*-repository)

    - fseq (package/source root)

        - reading 

        - reporting
        
        - tests (testings modules, not included in distribution)

    - scripts (run-scripts installed)

    - doc (sphinx-documentation)

The `setup.py` file was structured so that the scripts in the script folder
were installed as executionables so that the package can be run as a stand
alone command line program. 

A `MANIFEST.in` was created in accordance with ``distutil``'s recommendations
[distutil]_ to allow for distrubution of packages via the `setup.py` file.
The tests in the `testing` folder were purposely kept out of packaging as they
were not considered part of the deployment code, but rather the development
source code.

Design
......

The structure and interfaces of the classes kept as designed, making the
following basic types:

- ``SeqReader``

- ``SeqEncoder`` to encode data and manage format detection if not predefined.

  A specific subclass ``SeqEncoderGC`` was made to fulfill the goal of doing
  GC-analysis

- ``SeqFormat`` the object that detects specific formats for which three
  different formats are supported ``FastaSingleline``, ``FastaMultiline``,
  and ``FastQ``

- ``SeqFormatDetector`` to select which format an imput stream is.

- ``ReportBuilderBase`` the post-processing coordinator, for which two
  specific post-processors were created to allow ``fseq`` to produce usable
  fourier reports: ``ReportBuilderFFT`` and ``ReportBuilderPositionAverage``.

- ``ReportBase`` conforms with output producer, for which two specific
  graph producers (``LinePlot`` and ``HeatMap``) were created.

To comply with the general design criteria, all relevant classes are imported
into the package root such that the user only needs to use ``import fseq``.

Default behaviour is simple as the following is sufficient::

    >>> fseq.SeqReader(dataSourcePaths="some/path/to/file.fastq").run()

Further, full customization can be performed and expressed in a single line.
The expression can also be split to severao lines increase readability.

Unittests
.........

In total 78 different tests were created in four different files.
Each file corresponding to one of the four modules in the package.
A test exclusively tested one aspect of the functionality, but many of the tests
asserted more than one behaviour for that aspect.

For example, ``TestSeqFormatDetector.test_FormatUnknown`` that ascertains that
an exception is raised for when the detector runs out of available formats both
when it was initiated with and without a forced format.

Documentation
.............

All classes were fully documented as decided and several ``sphinx`` used to
produce a complete documentation with several supporting extra documents.

Results
-------

Technical results
.................

A run took less than 10 minutes on a standard Intel i5 desktop with 4GB
RAM and a 2TB HDD. Typically more than 100% CPU was used, though during
resizing of the array, a dipping of CPU was clear due to main thread waiting
for all threads to join. The memory usage peaked around 75% when using 16-bit
float point precision, in `numpy`.
With default settings, five report pdf:s were created for each file analysed.

The unittests typically ran for a fraction of a second and succeded in reporting
previously undetected errors as well as allerting to inconsistencies caused by
minor changes of interfaces during development.

Analysis of two files
.....................

Two real data files were analysed `Mysc_24_ATCACG_L008_R1_001.fastq` and
`Mysc_74_GTTTCG_L008_R1_001.fastq`.
The two files were multiplexed in the same Illumina MiSeq lane, but are two
distinct species.
Therefore, technical aspects of the sequencing can possibly be seen as
recurring features in the two, while aspects pertaining to the DNA in each
sample should be private.

As an example, the occurancy of undecided nucleotides is highly concurrent in
both data files:
:download:`Mysc 24 <Mysc_24_ATCACG_L008_R1_001.fastq.reports/average.lacking.line.pdf>`
:download:`Mysc 74 <Mysc_74_GTTTCG_L008_R1_001.fastq.reports/average.lacking.line.pdf>`

While the GC bias over the two files are distictly different:
:download:`Mysc 24 <Mysc_24_ATCACG_L008_R1_001.fastq.reports/average.not-lacking.line.pdf>`
:download:`Mysc 74 <Mysc_74_GTTTCG_L008_R1_001.fastq.reports/average.not-lacking.line.pdf>`

The `Myst 24` having a highly structured bias as averaged over the ~5M reads.

The random sample of 1000 reads, Fourier Transformed and clustered based on
their amplitudes show little obvious structure in their angles:

:download:`Mysc 24 <Mysc_24_ATCACG_L008_R1_001.fastq.reports/fft-sample.angle.heatmap.pdf>`
:download:`Mysc 74 <Mysc_74_GTTTCG_L008_R1_001.fastq.reports/fft-sample.angle.heatmap.pdf>`

While the corresponding amplitudes for the same 1000 reads share two clear
features. First, for the 0-frequency, an obvious large spread in overall GC
bias is evident with a small subset of around 90% GC a majority around 40-50
and another smaller cluster close to 0%. The second feature, which shows clearly
in both is that the 1/34 frequency and its neighbours behave distinctively.

:download:`Mysc 24 <Mysc_24_ATCACG_L008_R1_001.fastq.reports/fft-sample.abs.heatmap.pdf>`
:download:`Mysc 74 <Mysc_74_GTTTCG_L008_R1_001.fastq.reports/fft-sample.abs.heatmap.pdf>`

Discussion
----------

todo

References
----------

.. [c3se] http://www.c3se.chalmers.se/index.php/Python_and_High_Performance_Computing_2014
.. [distutil] https://docs.python.org/2/distutils/sourcedist.html#the-manifest-in-template
.. [tdd] http://en.wikipedia.org/wiki/Test-driven_development
.. [npd] https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#common-rest-concepts
.. [sphinx] http://sphinx-doc.org/
.. [rst] http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists
.. [fastqc] http://www.bioinformatics.babraham.ac.uk/projects/fastqc/

Appendix A: Project Plan
------------------------

The :download:`project plan<projectPlan.pdf>` submitted for the project.

Appendix B: Code
----------------

The current code is accessible from *Gitorious* at:

https://gitorious.org/fseq

Alternatively, each class implementation can be accessed here:

- :class:`fseq.reading`

    :class:`fseq.reading.seq_reader.SeqReader`

    :class:`fseq.reading.seq_encoder.SeqEncoder`

    :class:`fseq.reading.seq_encoder.SeqFormat`

        :class:`fseq.reading.seq_encoder.FastQ`

        :class:`fseq.reading.seq_encoder.FastaMultiline`

        :class:`fseq.reading.seq_encoder.FastaSingleline`
        
    :class:`fseq.reading.seq_encoder.SeqFormatDetector`

- :class:`fseq.reporting`

    :class:`fseq.reporting.reports.ReportBase`

        :class:`fseq.reporting.reports.HeatMap`

        :class:`fseq.reporting.reports.LinePlot`

    :class:`fseq.reporting.report_builder.ReportBuilderBase`

        :class:`fseq.reporting.report_builder.ReportBuilderFFT`

        :class:`fseq.reporting.report_builder.ReportBuilderPositionAverage`
