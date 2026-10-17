#!/usr/bin/env python3
# nuc-fan-rpm: read Intel NUC fan RPM from the EC memory window via /dev/mem (read-only).
# SPDX-License-Identifier: MIT
import os, sys, mmap, subprocess
BASE = 0xFE410000
def fail(r):
    print("ERR " + r); sys.exit(1)
try:
    v = subprocess.run(["setpci", "-s", "00:1f.0", "98.l"], capture_output=True, text=True, timeout=5).stdout.strip()
    if v:
        b = int(v, 16)
        if b & 1 and (b & ~0xFFFF) != 0:
            BASE = b & ~0xFFFF
        else:
            fail("LPC reg 98 unexpected: " + v)
except (FileNotFoundError, subprocess.TimeoutExpired):
    pass
except ValueError:
    fail("bad setpci output")
try:
    fd = os.open("/dev/mem", os.O_RDONLY | os.O_SYNC)
    m = mmap.mmap(fd, 0x1000, mmap.MAP_SHARED, mmap.PROT_READ, offset=BASE)
except Exception as e:
    fail("mmap: %s" % e)
try:
    d = m[0x400:0x420]
finally:
    m.close(); os.close(fd)
if not (d.startswith(b"SPG_EC") or d.startswith(b"ELM_EC")):
    fail("bad EC id %r" % d[:8])
if d[0x1A] != 1:
    fail("fan flag %d" % d[0x1A])
print((d[0x1B] << 8) | d[0x1C])
