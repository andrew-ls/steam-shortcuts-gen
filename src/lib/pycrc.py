#!/usr/bin/env python2
# encoding: utf-8

# This file is part of steam-shortcuts-gen.
#
# Copyright (c) 2006-2013 Thomas Pircher <tehpeh@gmx.net>
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


"""
CRC Bit by Bit algorithm implemented in Python.

This module can also be used as a library from within Python.

Examples
========

This is an example use of the algorithm:

>>> from pycrc import Crc
>>>
>>> crc = Crc(width = 16, poly = 0x8005,
...           reflect_in = True, xor_in = 0x0000,
...           reflect_out = True, xor_out = 0x0000)
>>> print("0x%x" % crc.bit_by_bit("123456789"))
"""

# Class Crc
###############################################################################
class Crc (object):
    """
    A base class for CRC routines.
    """

    # Class constructor
    ###############################################################################
    def __init__ (self, width, poly, reflect_in, xor_in, reflect_out, xor_out, table_idx_width = None):
        """The Crc constructor.

        The parameters are as follows:
            width
            poly
            reflect_in
            xor_in
            reflect_out
            xor_out
        """
        self.Width          = width
        self.Poly           = poly
        self.ReflectIn      = reflect_in
        self.XorIn          = xor_in
        self.ReflectOut     = reflect_out
        self.XorOut         = xor_out
        self.TableIdxWidth  = table_idx_width

        self.MSB_Mask = 0x1 << (self.Width - 1)
        self.Mask = ((self.MSB_Mask - 1) << 1) | 1
        if self.TableIdxWidth != None:
            self.TableWidth = 1 << self.TableIdxWidth
        else:
            self.TableIdxWidth = 8
            self.TableWidth = 1 << self.TableIdxWidth

        self.DirectInit = self.XorIn
        self.NonDirectInit = self.__get_nondirect_init(self.XorIn)
        if self.Width < 8:
            self.CrcShift = 8 - self.Width
        else:
            self.CrcShift = 0


    # function __get_nondirect_init
    ###############################################################################
    def __get_nondirect_init (self, init):
        """
        return the non-direct init if the direct algorithm has been selected.
        """
        crc = init
        for i in range(self.Width):
            bit = crc & 0x01
            if bit:
                crc^= self.Poly
            crc >>= 1
            if bit:
                crc |= self.MSB_Mask
        return crc & self.Mask


    # function reflect
    ###############################################################################
    def reflect (self, data, width):
        """
        reflect a data word, i.e. reverts the bit order.
        """
        x = data & 0x01
        for i in range(width - 1):
            data >>= 1
            x = (x << 1) | (data & 0x01)
        return x


    # function bit_by_bit
    ###############################################################################
    def bit_by_bit (self, in_str):
        """
        Classic simple and slow CRC implementation.  This function iterates bit
        by bit over the augmented input message and returns the calculated CRC
        value at the end.
        """
        register = self.NonDirectInit
        for c in in_str:
            octet = ord(c)
            if self.ReflectIn:
                octet = self.reflect(octet, 8)
            for i in range(8):
                topbit = register & self.MSB_Mask
                register = ((register << 1) & self.Mask) | ((octet >> (7 - i)) & 0x01)
                if topbit:
                    register ^= self.Poly

        for i in range(self.Width):
            topbit = register & self.MSB_Mask
            register = ((register << 1) & self.Mask)
            if topbit:
                register ^= self.Poly

        if self.ReflectOut:
            register = self.reflect(register, self.Width)
        return register ^ self.XorOut
