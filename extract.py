#!/usr/bin/env python2
from __future__ import print_function
import sys
import os
import pickle
import zlib
import struct
import pylzma
import dependencies as deps

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

if len(sys.argv) >= 2:

    d = open(sys.argv[1], "rb").read()

    index_len = struct.unpack("I", d[0:4])[0]
    c = d[4:4 + index_len]

    index = zlib.decompress(c)
    index = pickle.loads(index)

    if len(sys.argv) >= 3:
        for f in index:
            if ";rsum" in f[0]:
                break
            if f[0] == sys.argv[2]:
                os.umask(0)
                try:
                    fd = os.open(f[0], os.O_WRONLY | os.O_CREAT, f[1]["mode"])
                except OSError:
                    print("Cannot write to file")
                    exit(-1)
                block_count = struct.unpack("I", f[1]["cIdx"][0:4])[0]
                buf = b""
                pos = 4 + index_len + f[1]["index"][0]
                for i in xrange(block_count):
                    print("Extracting block %d / %d...       " % (i + 1, block_count), end="\r")
                    size = struct.unpack("I", f[1]["cIdx"][4 + i * 4:8 + i * 4])[0]
                    c = d[pos:pos + size]
                    buf += pylzma.decompress(c)
                    pos += size
                assert len(buf) == f[1]["uSz"]
                os.fdopen(fd, "wb").write(buf)
                print("Saved to %s                   " % f[0])
                exit(0)
        print("File not found")
    else:
        for f in index:
            if ";rsum" in f[0]:
                break
            print("%s  %8d  %8d %s" % (deps.stat.filemode(f[1]["mode"]), f[1]["cSz"], f[1]["uSz"], f[0]))

else:
    print("Usage: %s <RepairData.dat> [file]" % sys.argv[0])
