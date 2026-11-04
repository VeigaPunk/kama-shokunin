import hashlib,re,glob,os,sys
for p in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)),"anchors","S*.md"))): h,b=open(p,"rb").read().split(b"\n",1); print(("OK   " if re.search(rb"sha256=([0-9a-f]{64})",h).group(1).decode()==hashlib.sha256(b).hexdigest() else "FAIL ")+os.path.basename(p))
