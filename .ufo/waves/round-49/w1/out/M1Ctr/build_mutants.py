#!/usr/bin/env python3
"""Build 20 mutated copies of the C1 counter in scratch. Each mutant is produced
from a FRESH pristine copy with exactly one change. Mutations are expressed as
small functions over the line list; every mutant must compile.
Output: $M/M01.py .. $M/M20.py.
"""
import os
import py_compile

PRISTINE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py"
M = "/fast/scratch/hyaku/kama-r49/M1Ctr/mutants"
os.makedirs(M, exist_ok=True)
BASE = open(PRISTINE).read().splitlines(keepends=True)


def Ls(lines, fp, sub):
    hits = [i for i, l in enumerate(lines) if fp in l]
    assert len(hits) == 1, (fp, len(hits))
    i = hits[0]
    lines[i] = lines[i].rstrip("\n").replace(fp, sub) + "\n"


def Dg(lines, fp, count):
    hits = [i for i, l in enumerate(lines) if fp in l]
    assert len(hits) == 1, (fp, len(hits))
    del lines[hits[0]:hits[0] + count]


# M01: SERVER_SHA last hex char flipped
def m01(l):
    Ls(l, 'SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0"',
         'SERVER_SHA = "35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff1"')


# M02: MODEL_SHA last hex char flipped
def m02(l):
    Ls(l, 'MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"',
         'MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256e"')


# M03: MODEL_URL points at a non-existent GGUF (only the f-string line)
def m03(l):
    Ls(l, 'f"{MODEL_COMMIT}/tinyllamas/stories260K.gguf")',
         'f"{MODEL_COMMIT}/tinyllamas/stories260Kx.gguf")')


# M04: README_COMMIT zeroed -> README_URLS can't match any row
def m04(l):
    Ls(l, 'README_COMMIT = "caa8191df159f764fb0160e3d2fc6be008948aee"',
         'README_COMMIT = "0000000000000000000000000000000000000000"')


# M05: newrow leg diff is empty (BASE folded into tip)
def m05(l):
    Ls(l, "new = rows(tip) - rows(BASE)", "new = rows(tip) - rows(tip)")


# M06: met conjunction and -> or
def m06(l):
    Ls(l, "met = wl and cl and nl", "met = wl or cl or nl")


# M07: exe check skipped
def m07(l):
    Ls(l, "if exe != SERVER_SHA:", "if False:")


# M08: LISTEN ownership intersection dropped
def m08(l):
    Ls(l, "if not li or not (li & pid_socket_inodes(pid)):", "if not li:")


# M09: loopback-only address filter dropped
def m09(l):
    Dg(l, 'if addr not in ("0100007F"', 2)


# M10: -m model hash check skipped
def m10(l):
    Ls(l, "if sha_file(mpath) != MODEL_SHA:", "if False:")


# M11: piece-value comparison dropped (ids still checked)
def m11(l):
    hits = [i for i, x in enumerate(l) if 'bad = [t for t in tk if not (isinstance(t.get("piece")' in x]
    assert len(hits) == 1
    i = hits[0]
    l[i:i + 2] = ["        bad = []\n"]


# M12: /detokenize round-trip rule dropped
def m12(l):
    Dg(l, 'dt = post(port, "/detokenize"', 3)


# M13: witness.released accepted also when missing/false-ish
def m13(l):
    Ls(l, 'rr["witness"].get("released") is True)', 'rr["witness"].get("released") is not False)')


# M14: teardown pid_alive check dropped
def m14(l):
    Ls(l, 'if pid_alive(ready["pid"]) or not port_refuses(ready["port"]):',
         'if not port_refuses(ready["port"]):')


# M15: port_refuses returns True even when the port still accepts
def m15(l):
    hits = [i for i, x in enumerate(l) if 's.connect(("127.0.0.1", port))' in x]
    assert len(hits) == 1
    i = hits[0]
    l[i:i + 2] = ["        s.connect((\"127.0.0.1\", port))\n", "        return True\n"]


# M16: cap expected error prefix wrong (never matches)
def m16(l):
    Ls(l, 'err.startswith("provenance-member")', 'err.startswith("provenance-sparse")')


# M17: cap subprocess timeout ~0
def m17(l):
    Ls(l, "timeout=30)", "timeout=0.001)")


# M18: positive control always judged good
def m18(l):
    Ls(l, 'good_case = executed and not (isinstance(err, str) and err.startswith("provenance-"))',
         "good_case = True")


# M19: newrow leg drops the base diff
def m19(l):
    Ls(l, "new = rows(tip) - rows(BASE)", "new = rows(tip)")


# M20: /tokenize substring requirement dropped
def m20(l):
    Ls(l, 'and "/tokenize" in ln]', "and (True)]  # M20: /tokenize substring requirement removed")


MUT = {f"M{k:02d}": fn for k, fn in enumerate(
    [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10,
     m11, m12, m13, m14, m15, m16, m17, m18, m19, m20], 1)}
for name, fn in sorted(MUT.items()):
    lines = list(BASE)
    fn(lines)
    src = "".join(lines)
    out = os.path.join(M, name + ".py")
    open(out, "w").write(src)
    py_compile.compile(out, doraise=True)
    print(name, "ok")
print("wrote", len(MUT), "mutants, all compile")
