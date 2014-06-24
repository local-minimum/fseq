#!/usr/bin/env python
"""Reporting-related modules of fseq.

The sub-package contains `report_builder` which post-processes data and
sends it off to make various `reports`.

The builders contains no graphics information, but simply prepares data.
A new builder should be written if a new type of analysis is needed based
on an abstraction of the data that is not already present in any of the
previous builders.

A report makes an image from data sent to it from the builder.
Purpose of breaking this out is to allow for changing library that produces
the reports and to allow for quick reuse with similar graphics for identical
types of graphs for several report-builders.
"""
