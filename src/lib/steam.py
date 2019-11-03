#!/usr/bin/env python2
# encoding: utf-8

# This file is part of steam-shortcuts-gen.
#
# Copyright (c) 2012, 2013 Scott Rice
#
# SPDX-License-Identifier: MIT
#
# The MIT License:
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
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
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pycrc import Crc

def filename_for_shortcut (name, target):
    """
    Calculates the filename for a given shortcut. This filename is a 64bit
    integer, where the first 32bits are a CRC32 based off of the name and
    target (with the added condition that the first bit is always high), and
    the last 32bits are 0x02000000.
    """
    # This will seem really strange (where I got all of these values), but I
    # got the xor_in and xor_out from disassembling the steamui library for
    # OSX. The reflect_in, reflect_out, and poly I figured out via trial and
    # error.
    algorithm = Crc(
        width = 32,
        poly = 0x04C11DB7,
        reflect_in = True,
        xor_in = 0xffffffff,
        reflect_out = True,
        xor_out = 0xffffffff
    )
    input_string = ''.join([target,name])
    top_32 = algorithm.bit_by_bit(input_string) | 0x80000000
    full_64 = (top_32 << 32) | 0x02000000
    print str(full_64)
