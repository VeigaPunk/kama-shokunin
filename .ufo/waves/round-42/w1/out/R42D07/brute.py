#!/usr/bin/env python3
"""R42D07: bounded brute-force for the M10 probe — find bytes whose SHA-256
shares the first 8 hex chars of the cited digest 753bfa73... but differs
overall. 8 workers, ~10 min cap; writes the file and reports."""
import hashlib, multiprocessing as mp, os, sys

TARGET = "753bfa73"
OUT = "/fast/scratch/kama-r42/seats/R42D07/probe-m10.bin"

def hunt(rng):
    pre = b"r42d07-m10-probe "
    for i in range(rng, 4_000_000_000, 8):
        if hashlib.sha256(pre + str(i).encode()).hexdigest().startswith(TARGET):
            return i
    return None

def main():
    with mp.Pool(8) as p:
        for r in p.imap_unordered(hunt, range(8)):
            if r is not None:
                data = b"r42d07-m10-probe " + str(r).encode()
                h = hashlib.sha256(data).hexdigest()
                assert h.startswith(TARGET) and h != TARGET + "0" * 56
                with open(OUT, "wb") as f:
                    f.write(data)
                print(f"FOUND nonce={r} sha256={h} prefix={TARGET} bytes={len(data)}")
                p.terminate()
                return 0
    print("NOT-FOUND within cap")
    return 1

if __name__ == "__main__":
    sys.exit(main())
