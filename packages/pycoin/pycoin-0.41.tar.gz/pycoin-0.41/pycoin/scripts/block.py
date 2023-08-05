#!/usr/bin/env python

import argparse
import binascii
import datetime

from pycoin.block import Block
from pycoin.scripts.tx import dump_tx
from pycoin.serialize import b2h_rev, stream_to_bytes


def dump_block(block, network):
    blob = stream_to_bytes(block.stream)
    print("%d bytes   block hash %s" % (len(blob), block.id()))
    print("version %d" % block.version)
    print("prior block hash %s" % b2h_rev(block.previous_block_hash))
    print("merkle root %s" % binascii.hexlify(block.merkle_root).decode("utf8"))
    print("timestamp %s" % datetime.datetime.utcfromtimestamp(block.timestamp).isoformat())
    print("difficulty %d" % block.difficulty)
    print("nonce %s" % block.nonce)
    print("%d transaction%s" % (len(block.txs), "s" if len(block.txs) != 1 else ""))
    for idx, tx in enumerate(block.txs):
        print("Tx #%d:" % idx)
        dump_tx(tx, netcode=network)


def main():
    parser = argparse.ArgumentParser(description="Dump a block in human-readable form.")
    parser.add_argument("block_bin", nargs="+", type=argparse.FileType('rb'),
                        help='The file containing the binary block.')

    args = parser.parse_args()

    for f in args.block_bin:
        block = Block.parse(f)
        dump_block(block, network='M')
        print('')

if __name__ == '__main__':
    main()
