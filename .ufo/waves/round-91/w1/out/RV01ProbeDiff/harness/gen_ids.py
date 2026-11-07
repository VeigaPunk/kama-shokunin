#!/usr/bin/env python3
"""Generate norm/ids.txt: edge-case ids plus deterministic random bulk."""
import random
from pathlib import Path

fixed = [
    b"good", b"/models/sub/good.gguf", b"good.gguf.gguf", b".gguf", b"..gguf", b"x.GGUF",
    b".GGUF", b".Gguf", b"a.gguf/", b"a.gguf//", b"/", b"//", b"a/", b"a//b", b"///a///b/",
    b"/gguf", b"good.GGUF", b"good.gguf ", b" good.gguf", b"\tgood.gguf", b"good\t.gguf",
    b"gguf.", b".ggufs", b"good.ggf", b"good.ggufx", b"5.gguf", b"a\\bgguf", b"q\"b\\s",
    b"\\u001bgood", b"\x1bgood", b"\rgood", b"good\r", b"a b", b" leading and trailing ",
    "モデル/na.me.gguf".encode(), "модель".encode(), "𝄞".encode(), "café.gguf".encode(),
    b"\xff\xfeabc.gguf", b"\x80.gguf", b"abc\xff", b"a/\xffb", b"\xff", b"/.gguf", b"a/.gguf",
    b"a/b.GGUF", b"1.0", b"1", b"01", b"0x10", b"16", b"1e3", b"1000", b"1E3", b"1e-3",
    b"nan", b"inf", b"+5", b"-5", b".5", b"5.", b"0", b"00", b"-", b"--", b"*",
    b"a/b/c/d/e/f.gguf", b"x/1e3", b"1e3/1000", b"1000/1e3", b"a%b", b"a=b", b"a:b", b"a'b",
    b'a"b', b"a\\b.gguf", b"\\", b"\\\\", b".gguf.gguf", b"gguf", b"a.gguf.gguf", b" 1e3",
    b"1e3 ", b"", b" ", b"  ",
]

rng = random.Random(91)
alpha = b"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
weird = b"\xff\xfe\x80\xc3\xa9"

def rid():
    r = rng.random()
    n = rng.randint(1, 24)
    s = bytes(rng.choice(alpha) for _ in range(n))
    if r < 0.15:
        s = s + b"/" + bytes(rng.choice(alpha) for _ in range(rng.randint(0, 8)))
    elif r < 0.25:
        s = bytes(rng.choice(alpha) for _ in range(rng.randint(0, 8))) + b"/" + s
    if rng.random() < 0.12:
        s += b".gguf"
    if rng.random() < 0.05:
        s += b"/"
    if rng.random() < 0.03:
        s += bytes(rng.choice(weird) for _ in range(rng.randint(1, 3)))
    if rng.random() < 0.02:
        s = str(rng.randint(0, 10**6)).encode()
    if rng.random() < 0.01:
        s = ("%e" % (rng.random() * 10**6)).encode()
    return s.replace(b"\n", b"").replace(b"\x00", b"")

out = Path(__file__).resolve().parent / "ids.txt"
with out.open("wb") as f:
    for s in fixed:
        f.write(s + b"\n")
    for _ in range(200000):
        f.write(rid() + b"\n")
print("ids:", out, "lines:", len(fixed) + 200000)
