# -*- coding: utf-8 -*-
# The MIT License (MIT)
#
# Copyright © 2014 Tim Bielawa <timbielawa@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


"""
Test for NIST prefix guessing
"""

import unittest
from . import TestCase
import bitmath


class TestBestPrefixNIST(TestCase):
    ##################################################################
    # These tests verify guessing for cases where the best
    # representation is only one order of magnitude different.

    def test_simple_round_up(self):
        """NIST: 1 GiB (as a MiB()) rounds up into a GiB()"""
        # Represent a Gibibyte as a large MiB
        GiB_in_MiB = bitmath.MiB(1024)
        # This should turn into a GiB
        self.assertIs(type(GiB_in_MiB.best_prefix()), bitmath.GiB)

    def test_simple_round_down(self):
        """NIST: 1 MiB (as a GiB()) rounds down into a MiB()"""
        # Represent one MiB as a small GiB
        MiB_in_GiB = bitmath.GiB(bytes=1048576)
        # This should turn into a MiB
        self.assertIs(type(MiB_in_GiB.best_prefix()), bitmath.MiB)

    ##################################################################
    # These tests verify guessing for cases where the best
    # representation is more than one order of magnitude different.

    def test_multi_oom_round_up(self):
        """NIST: A very large Kibibyte rounds up into a Pibibyte"""
        large_KiB = bitmath.KiB.from_other(bitmath.PiB(1))
        self.assertIs(type(large_KiB.best_prefix()), bitmath.PiB)

    def test_multi_oom_round_down(self):
        """NIST: A very small Pibibyte rounds down into a KibiByte"""
        small_PiB = bitmath.PiB.from_other(bitmath.KiB(1))
        self.assertIs(type(small_PiB.best_prefix()), bitmath.KiB)

    ##################################################################
    # These tests mirror the multi_oom ones, except for extreme cases
    # where even the largest unit available results in values with
    # more than 4 digits left of the radix point.

    def test_extreme_oom_round_up(self):
        """NIST: 2048 EiB (as a KiB()) rounds up into an EiB()"""
        huge_KiB = bitmath.KiB.from_other(bitmath.EiB(1))
        self.assertIs(type(huge_KiB.best_prefix()), bitmath.EiB)

    def test_extreme_oom_round_down(self):
        """NIST: 1 Bit (as a EiB()) rounds down into a Bit()"""
        tiny_EiB = bitmath.EiB.from_other(bitmath.Bit(1))
        self.assertIs(type(tiny_EiB.best_prefix()), bitmath.Bit)
