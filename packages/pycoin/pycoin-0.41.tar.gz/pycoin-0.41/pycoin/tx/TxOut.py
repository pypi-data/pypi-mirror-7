# -*- coding: utf-8 -*-
"""
Deal with the part of a Tx that specifies where the Bitcoin goes to.


The MIT License (MIT)

Copyright (c) 2013 by Richard Kiss

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from ..convention import satoshi_to_mbtc
from ..encoding import bitcoin_address_to_hash160_sec_with_prefix, hash160_sec_to_bitcoin_address

from ..serialize import b2h
from ..serialize.bitcoin_streamer import parse_struct, stream_struct

from .script import tools
from .script.solvers import hash160_for_script


class TxOut(object):
    """
    The part of a Tx that specifies where the Bitcoin goes to.
    """
    def __init__(self, coin_value, script):
        self.coin_value = int(coin_value)
        self.script = script

    def stream(self, f):
        stream_struct("QS", f, self.coin_value, self.script)

    @classmethod
    def parse(self, f):
        return self(*parse_struct("QS", f))

    def __str__(self):
        return 'TxOut<%s mbtc "%s">' % (satoshi_to_mbtc(self.coin_value), tools.disassemble(self.script))

    def bitcoin_address(self, address_prefix=b'\0'):
        # attempt to return the destination address, or None on failure
        hash160 = self.hash160()
        if hash160:
            return hash160_sec_to_bitcoin_address(hash160, address_prefix=address_prefix)
        return None

    def hash160(self):
        # attempt to return the destination address, or None on failure
        return hash160_for_script(self.script)


def standard_tx_out_script(bitcoin_address):
    STANDARD_SCRIPT_OUT = "OP_DUP OP_HASH160 %s OP_EQUALVERIFY OP_CHECKSIG"
    hash160, prefix = bitcoin_address_to_hash160_sec_with_prefix(bitcoin_address)
    script_text = STANDARD_SCRIPT_OUT % b2h(hash160)
    return tools.compile(script_text)
