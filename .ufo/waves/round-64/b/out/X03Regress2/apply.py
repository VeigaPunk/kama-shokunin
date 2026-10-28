import sys
tree, tsv = sys.argv[1], sys.argv[2]
for line in open(tsv):
    cap, path, find, rep = line.rstrip("\n").split("\t")
    p = f"{tree}/{path}"
    s = open(p).read()
    n = s.count(find)
    print(cap, "occurrences", n)
    assert n == 1
    open(p, "w").write(s.replace(find, rep))
