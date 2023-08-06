# The MIT License (MIT)
#
# Copyright (c) 2014 Richard Moore
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import sys
sys.path.append('../pyaes')

import os
import random

import pyaes
from pyaes.blockfeeder import Decrypter, Encrypter

from pyaes.util import to_bufferable


key = os.urandom(32)

plaintext = os.urandom(1000)

for mode_name in pyaes.AESModesOfOperation:
    mode = pyaes.AESModesOfOperation[mode_name]
    print(mode.name)

    kw = dict(key = key)
    if mode_name in ('cbc', 'cfb', 'ofb'):
        kw['iv'] = os.urandom(16)

    encrypter = Encrypter(mode(**kw))
    ciphertext = to_bufferable('')

    # Feed the encrypter random number of bytes at a time
    index = 0
    while index < len(plaintext):
        length = random.randint(1, 128)
        if index + length > len(plaintext): length = len(plaintext) - index
        ciphertext += encrypter.feed(plaintext[index: index + length])
        index += length
    ciphertext += encrypter.feed(None)

    decrypter = Decrypter(mode(**kw))
    decrypted = to_bufferable('')

    # Feed the decrypter random number of bytes at a time
    index = 0
    while index < len(ciphertext):
        length = random.randint(1, 128)
        if index + length > len(ciphertext): length = len(ciphertext) - index
        decrypted += decrypter.feed(ciphertext[index: index + length])
        index += length
    decrypted += decrypter.feed(None)

    passed = decrypted == plaintext
    cipher_length = len(ciphertext)
    print("  cipher-length=%(cipher_length)s passed=%(passed)s" % locals())
