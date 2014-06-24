Tutorial
========

Installing
----------

The program is installed for current user by running::

    $ python setup.py install --user

Or for all users by running::

    $ sudo python setup.py install

The following dependencies needs to be installed seperately::

    numpy, scipy, matplotlib

On debian systems copy::

    $ sudo apt-get update && sudo apt-get install python-numpy python-scipy python-matplotlib

Command Line Use
----------------

The following example runs default analysis on two different files::

    $ fseq ~/Data/Mysc_24_ATCACG_L008_R1_001.fastq ~/Data/Mysc_74_GTTTCG_L008_R1_001.fastq
    14-06-23 17:55 SeqReader    INFO     Has 2 jobs
    14-06-23 17:55 SeqReader    INFO     Reading: /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq
    14-06-23 17:57 SeqReader    INFO     Reading Complete: /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq
    14-06-23 17:57 SeqReader    INFO     Reporting <class 'fseq.reporting.report_builder.ReportBuilderFFT'> with args=("<type 'numpy.ndarray'>.shape=(4831521, 101)",), kwargs={'outputRoot': '/home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports'}
    14-06-23 17:57 SeqReader    INFO     Reporting <class 'fseq.reporting.report_builder.ReportBuilderPositionAverage'> with args=("<type 'numpy.ndarray'>.shape=(4831521, 101)",), kwargs={'outputRoot': '/home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports'}
    14-06-23 17:57 SeqReader    INFO     Reading: /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq
    Saving -> /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports/fft-sample.abs.heatmap.pdf
    Saving -> /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports/average.total.line.pdf
    Saving -> /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports/fft-sample.angle.heatmap.pdf
    14-06-23 18:01 SeqReader    INFO     Reading Complete: /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq
    14-06-23 18:01 SeqReader    INFO     Reporting <class 'fseq.reporting.report_builder.ReportBuilderFFT'> with args=("<type 'numpy.ndarray'>.shape=(5634723, 101)",), kwargs={'outputRoot': '/home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports'}
    14-06-23 18:01 SeqReader    INFO     Reporting <class 'fseq.reporting.report_builder.ReportBuilderPositionAverage'> with args=("<type 'numpy.ndarray'>.shape=(5634723, 101)",), kwargs={'outputRoot': '/home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports'}
    14-06-23 18:01 SeqReader    INFO     Waiting for 4 report builders to finish
    Saving -> /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports/average.total.line.pdf
    Saving -> /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports/fft-sample.abs.heatmap.pdf
    Saving -> /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports/fft-sample.angle.heatmap.pdf
    Saving -> /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports/average.lacking.line.pdf
    Saving -> /home/martin/Data/Mysc_24_ATCACG_L008_R1_001.fastq.reports/average.not-lacking.line.pdf
    Saving -> /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports/average.lacking.line.pdf
    Saving -> /home/martin/Data/Mysc_74_GTTTCG_L008_R1_001.fastq.reports/average.not-lacking.line.pdf
    14-06-23 18:03 SeqReader    INFO     All jobs complete`

**Note:** Running above consumes quite a lot of memory and cpu and takes about
10 minutes.

**Note:** If ``fseq`` is not found on your system, it usually is due to the 
default target of scripts for user install is not in your PATH.
To ammend this, check where install copied the file `scripts/fseq` and append
that to your current PATH.

Python Use
----------

For all scenarios it should suffice to import the package:

>>> import fseq

To create a reader that will run the analysis:

>>> r = fseq.SeqReader(dataSourcePaths=("~/Data/Mysc_24_ATCACG_L008_R1_001.fastq", "~/Data/Mysc_74_GTTTCG_L008_R1_001.fastq"))

We can see how many jobs the reader has left:

>>> len(r)
2

And we can see the encoding that will be performed (and change it):

>>> r.seqEncoder
<fseq.reading.seq_encoder.SeqEncoderGC at 0x7fa9f9539b10>

This encoder is the default and will translate Gs and Cs to 1 while As and Ts
are made into 0s.

We can also see which reports were requested by the encoder and thus added to
the reader since we didn't say what reports we wanted:

>>> tuple(r.reportBuilders)
(<fseq.reporting.report_builder.ReportBuilderFFT at 0x7fa9f95399d0>,
 <fseq.reporting.report_builder.ReportBuilderPositionAverage at 0x7fa9f9539c50>)

To run encoding and produce results, simply:

>>> r.run()

Note that this will take some time and consume quite a lot of resoursece.
It took about 10 minutes on a standard desktop for the two files in the 
command line example, and the python use is no different.
