import re, sys, difflib
VAR = [
    (re.compile(r"pid \d+"), "pid <PID>"),
    (re.compile(r"port \d+"), "port <PORT>"),
    (re.compile(r"nonce 'kama witness [0-9a-f]+'"), "nonce 'kama witness <NONCE>'"),
    (re.compile(r"inode \d+ recorded"), "inode <INODE> recorded"),
    (re.compile(r"'inode': '\d+'"), "'inode': '<INODE>'"),
    (re.compile(r"sealed image \('\d+:\d+', '\d+'\)"), "sealed image ('<DEV>', '<INODE>')"),
    (re.compile(r"00:01:\d+ seals"), "<MEMDEV>:<MEMINO> seals"),
    (re.compile(r"after [\d.]+ s"), "after <T> s"),
    (re.compile(r"/fast/scratch/[^ ']*?/work-b(\d)"), "<SCRATCH>/work-b\\1"),
]
def norm(path):
    out = []
    for ln in open(path):
        ln = ln.rstrip("\n")
        if ln.startswith("$ "):
            continue            # shell header: transcript decoration, not counter output
        for rx, rep in VAR:
            ln = rx.sub(rep, ln)
        out.append(ln)
    return out
a, b = norm(sys.argv[1]), norm(sys.argv[2])
na, nb = sys.argv[3], sys.argv[4]
print(f"lines {na}={len(a)} {nb}={len(b)}")
d = list(difflib.unified_diff(a, b, na, nb, lineterm="", n=0))
print("AGREE line by line after normalizing only variable fields" if not d else "\n".join(d))
for i, (x, y) in enumerate(zip(a, b), 1):
    print(f"  L{i:02d} {'==' if x == y else '!='} {x[:150]}")
