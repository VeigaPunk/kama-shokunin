#!/usr/bin/env python3
"""F02C1ShowEndpoint: generate two patched copies of the pristine tool (scratch only).

p1 (A09-H3 faithful): the show capture request goes to /api/showX; the genuine,
unpatched Ollama server answers 404 for the unknown path -- i.e. the server fault
"show endpoint returns 404" while every other endpoint remains genuine.
p2 (fault-injection equivalence): the genuine /api/show request is kept, but the
captured status/body are rewritten to a 404 error body after the request.
"""
import pathlib

SRC = pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-live.py')
S = pathlib.Path('/fast/scratch/hyaku/kama-r60/F02C1ShowEndpoint')

src = SRC.read_text()

# p1: URL patch -> real server 404
a1 = "st, raw = http_call(port, 'POST', '/api/show', {'model': qualified})"
assert src.count(a1) == 1, f'anchor1 count {src.count(a1)}'
p1 = src.replace(a1, a1.replace("'/api/show'", "'/api/showX'"))
(S / 'trees/p1/tools/kama-ollama-live.py').write_text(p1)

# p2: genuine request, captured status/body rewritten to 404
a2 = "receipt['captures']['show'] = capture('show', st, raw)"
assert src.count(a2) == 1, f'anchor2 count {src.count(a2)}'
inject = (
    "receipt['captures']['show'] = capture('show', st, raw)\n"
    "        st = 404\n"
    "        raw = b'{\"error\":\"F02C1-injected-not-found\"}'\n"
    "        receipt['captures']['show'] = capture('show', st, raw)"
)
p2 = src.replace(a2, inject)
(S / 'trees/p2/tools/kama-ollama-live.py').write_text(p2)

import hashlib
for name in ('base', 'p1', 'p2'):
    f = S / f'trees/{name}/tools/kama-ollama-live.py'
    print(name, hashlib.sha256(f.read_bytes()).hexdigest())
