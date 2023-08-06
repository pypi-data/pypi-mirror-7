#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2012-2014 CNRS (Hervé BREDIN - http://herve.niderb.fr)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE S PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals

"""
Support for UEM file format

UEM (Unpartitioned Evaluation Map) is a file format used
to create an index specifying time regions within a recorded
waveform.

References
----------
http://www.itl.nist.gov/iad/mig/tests/rt/
"""

from pyannote.core import Segment
from base import BaseTextualTimelineParser


class UEMParser(BaseTextualTimelineParser):

    def _comment(self, line):
        return line[:2] == ';;'

    def _parse(self, line):

        tokens = line.split()
        # uri channel start end

        uri = str(tokens[0])
        #channel = tokens[1]
        start_time = float(tokens[2])
        end_time = float(tokens[3])
        segment = Segment(start=start_time, end=end_time)

        return segment, uri

    def _append(self, timeline, f, uri):

        format = '%s 1 %%g %%g\n' % (uri)
        for segment in timeline:
            f.write(format % (segment.start, segment.end))
