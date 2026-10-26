#!/usr/bin/env python3
"""R2Compare harness C: build a fixture repo and run the FROZEN counter
round48-live-replay-v5-audit.py against it.

The fixture receipts are byte-copies of the lane's real receipt-1 except:
  alias, captures.models.body, captures.models.body_sha256.
  receipt-1: control (real body both sides)
  receipt-2: F2 pair  - orig body '"unparseable"', rerun (fake live) '{bad json'
  receipt-3: F1 pair  - orig body 'null',          rerun (fake live) '5'
Expected: the tool passes receipt-2 (exit 0) and the counter's own projection
check fires; the tool fails receipt-3 (exit 1) and the counter's projection
stays silent (masked leniency).
"""
import hashlib, json, os, shutil, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
S = "/fast/scratch/hyaku/kama-r48/R2Compare"
FX = os.path.join(S, "fx")
OUT = LANE + "/.ufo/waves/round-48/w1/out/R2Compare"

FAKE_LIVE = '''#!/usr/bin/env python3
"""FAKE kama-llamacpp-live for the R2Compare fixture (NOT the lane tool).

Replay path (no --ready-timeout): emits a v5 receipt from the committed
template with the models body chosen by --alias (r1 real body, r2 '{bad json',
r3 '5'). Recordcheck path (--ready-timeout present): implements the record-time
contract offline and executes the stub server so the marker is written.
"""
import hashlib, json, os, re, subprocess, sys, tarfile

a = sys.argv
o = a[a.index('--out') + 1] if '--out' in a else None
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()

if '--ready-timeout' in a:
    need = ['--server', '--model', '--model-sha256', '--server-asset-url',
            '--server-asset-sha256', '--server-member', '--model-url', '--server-archive']
    if o is None or any(f not in a for f in need):
        sys.exit(2)
    au, asha = a[a.index('--server-asset-url') + 1], a[a.index('--server-asset-sha256') + 1]
    mu = a[a.index('--model-url') + 1]
    if not (au.startswith('https://') and mu.startswith('https://')):
        sys.exit(2)
    if not re.search(r'/resolve/[0-9a-f]{40}/', mu):
        sys.exit(2)
    arc = a[a.index('--server-archive') + 1]
    if sha(arc) != asha:
        sys.exit(2)
    mem, srv = a[a.index('--server-member') + 1], a[a.index('--server') + 1]
    with tarfile.open(arc) as tf:
        member = tf.extractfile(mem).read()
    if hashlib.sha256(member).hexdigest() != sha(srv):
        sys.exit(2)
    subprocess.run([srv])
    json.dump({'schema': 'kama-llamacpp-live/v5', 'outcome': 'pass'}, open(o, 'w'))
    sys.exit(0)

tpl = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.fake-template.json')))
alias = a[a.index('--alias') + 1]
srv, mdl = a[a.index('--server') + 1], a[a.index('--model') + 1]
arc = a[a.index('--server-archive') + 1]
murl = a[a.index('--model-url') + 1]
commit = re.search(r'/resolve/([0-9a-f]{40})/', murl).group(1)
BODY = {'r1': tpl['captures']['models']['body'], 'r2': '{bad json', 'r3': '5'}[alias]
r = json.loads(json.dumps(tpl))
r['alias'] = alias
r['started_utc'] = r['ended_utc'] = '2030-01-01T00:00:00Z'
r['server'] = dict(tpl['server'], sha256=sha(srv), realpath=srv)
r['model'] = dict(tpl['model'], sha256=sha(mdl), path=mdl)
r['provenance'] = {'server': {'asset_url': a[a.index('--server-asset-url') + 1],
                              'asset_sha256': a[a.index('--server-asset-sha256') + 1],
                              'member': a[a.index('--server-member') + 1]},
                   'model': {'url': murl, 'commit': commit, 'sha256': sha(mdl)},
                   'verified': {'at': 'record', 'archive_sha256': sha(arc),
                                'member_sha256': sha(srv), 'model_sha256': sha(mdl)}}
r['captures']['models']['body'] = BODY
r['captures']['models']['body_sha256'] = hashlib.sha256(BODY.encode()).hexdigest()
json.dump(r, open(o, 'w'))
'''

SOURCES = """# fixture SOURCES (newrow leg only)
| S999 | fixture pinned model | https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf | fixture |
"""

os.makedirs(OUT, exist_ok=True)
if os.path.exists(FX):
    shutil.rmtree(FX)
tpl = json.load(open(LANE + "/.ufo/waves/round-48/c2/live/receipt-1.json"))
os.makedirs(os.path.join(FX, "tools"))
os.makedirs(os.path.join(FX, ".ufo/waves/round-48/c2/live"))
os.makedirs(os.path.join(FX, "corpus"))
shutil.copy(S + "/tool-at-tip.py", FX + "/tools/kama-live-replay.py")
open(FX + "/tools/kama-llamacpp-live.py", "w").write(FAKE_LIVE)
json.dump(tpl, open(FX + "/tools/.fake-template.json", "w"))
open(FX + "/corpus/SOURCES.md", "w").write(SOURCES)

BODIES = {"receipt-1.json": None, "receipt-2.json": '"unparseable"', "receipt-3.json": "null"}
ALIASES = {"receipt-1.json": "r1", "receipt-2.json": "r2", "receipt-3.json": "r3"}
for name, body in BODIES.items():
    r = json.loads(json.dumps(tpl))
    r["alias"] = ALIASES[name]
    if body is not None:
        r["captures"]["models"]["body"] = body
        r["captures"]["models"]["body_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    json.dump(r, open(os.path.join(FX, ".ufo/waves/round-48/c2/live", name), "w"))

def git(*args):
    p = subprocess.run(["git", "-C", FX, *args], capture_output=True, text=True)
    assert p.returncode == 0, f"git {args}: {p.stderr}"
    return p.stdout.strip()

subprocess.run(["git", "init", "-q", FX], check=True)
top = git("rev-parse", "--show-toplevel")
assert top == FX, f"toplevel {top} != {FX}"
git("add", "-A")
git("-c", "user.name=R2Compare-fixture", "-c", "user.email=r2c@fixture.invalid",
    "commit", "-q", "-m", "fixture: projection disagreement pairs")
tip = git("rev-parse", "HEAD")
print("fixture tip:", tip)
open(OUT + "/fixture-tip.txt", "w").write(tip + "\n")
print(tip)
