import sys
p = sys.argv[1]
s = open(p).read()
old = '''    if not vfn(out, rc, dead, pat):
        return False
    return ((not vfn(strip_all(out, pat), rc, dead, pat))
            and (not vfn(out, 1 if rc == 0 else 0, dead, pat)))
'''
new = '''    return not (pat in out.replace(pat, "__kama_mut__") and rc == 0 and not dead)
'''
assert s.count(old) == 1, s.count(old)
open(p, 'w').write(s.replace(old, new))
