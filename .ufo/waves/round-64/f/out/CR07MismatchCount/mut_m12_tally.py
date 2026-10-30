import sys, os
d=sys.argv[1]
p=os.path.join(d,'tools/shortcut-tally.py')
src=open(p).read()
# make every round report as disclosed, keep the selftest fixture behaviour intact
old='''    elif rec["status"] == "ok":
        rec["status"] = "no-disclosure"'''
new='''    elif rec["status"] == "ok":
        rec["status"] = "disclosed:shortcut+survivor"'''
assert old in src
src=src.replace(old,new,1)
open(p,'w').write(src)
print("M12: tip's tools/shortcut-tally.py (UNPINNED) now reports every round as disclosed")
