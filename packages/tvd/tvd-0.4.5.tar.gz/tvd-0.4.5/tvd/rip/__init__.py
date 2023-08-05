#!/usr/bin/env python
# encoding: utf-8

#
# The MIT License (MIT)
#
# Copyright (c) 2013-2014 CNRS (Hervé BREDIN -- http://herve.niderb.fr/)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

__all__ = [
    "TVSeriesDVDSet"
    "Vobcopy",
    "HandBrakeCLI",
    "MEncoder",
    "VobSub2SRT",
    "LSDVD",
    "SndFileResample",
    "AVConv",
]

from tvd.rip.dvd import TVSeriesDVDSet
from tvd.rip.vobcopy import Vobcopy
from tvd.rip.handbrake import HandBrakeCLI
from tvd.rip.mencoder import MEncoder
from tvd.rip.vobsub2srt import VobSub2SRT
from tvd.rip.lsdvd import LSDVD
from tvd.rip.sndfile_resample import SndFileResample
from tvd.rip.avconv import AVConv

