#!/usr/bin/env python3
"""Replay only KQ23's M8 reset/read/window conjunct, NOT semantic claim admission."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
L=Path(__file__).resolve().parents[3]
rev='e75cf680b53484a61709ee1b2787d8dbc6419f74'
blob=subprocess.check_output(['git','-C',str(L),'show',rev+':corpus/SOURCES.md'])
rows={p[0]:p for line in blob.decode().splitlines() if line.startswith('| S')
      for p in [[x.strip() for x in line.strip().strip('|').split('|')]]}
def m8_component(anchor, teaches):
    # Limited citation grammar of these retained controls. A human still judges
    # whether the prose accounts for the reset and whether stronger assumptions hold.
    read=bool(re.search(r'141-143',anchor))
    reset=bool(re.search(r'278-280',anchor)) and 'running = true' in anchor
    window=all(t in teaches for t in ('after install','before','resets','lost'))
    return read and reset and window
cases=[('S043',rows['S043'][5],rows['S043'][6],False),
       ('S047-necessary-condition',rows['S047'][5],rows['S047'][6],True),
       ('S047-reset-citation-removed',rows['S047'][5].replace('278-280','omitted'),rows['S047'][6],False)]
results=[{'id':n,'expected':want,'observed':m8_component(a,t),
          'finding':'reset_read_window_covered' if m8_component(a,t) else 'reset_read_window_missing'}
         for n,a,t,want in cases]
doc={'schema':'kama-kq23-m8-controls/v1','revision':rev,
     'source_blob_sha256':hashlib.sha256(blob).hexdigest(),
     'limit':'Citation/component regression controls; not an NLP validator or proof all calls are read.',
     'cases':results,'passed':all(r['expected']==r['observed'] for r in results)}
print(json.dumps(doc,indent=1));sys.exit(0 if doc['passed'] else 1)
