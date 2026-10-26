import sys, re
def excerpt(lines, a, b):
    return "\n".join(x.strip() for x in lines[a-1:b] if x.strip())
def load(p): return open(p).read().splitlines()
pin, rel = load(sys.argv[1]), load(sys.argv[2])
pr = [tuple(int(y) for y in x.split('-')) if '-' in x else (int(x), int(x)) for x in sys.argv[3].split(',')]
rr = [None if x == '-' else (tuple(int(y) for y in x.split('-')) if '-' in x else (int(x), int(x))) for x in sys.argv[4].split(',')]
for p, r in zip(pr, rr):
    pe = excerpt(pin, *p)
    re_ = None if r is None else excerpt(rel, *r)
    print(f"PIN {p[0]}-{p[1]} ({len(pe.splitlines())} nonblank) vs REL {r}: eq={pe==re_}", 'nw_pin=', len(re.sub(r'\s','', ''.join(pin[p[0]-1:p[1]]))))
    if pe != re_:
        print('---PIN---'); print(pe); print('---REL---'); print(re_)
