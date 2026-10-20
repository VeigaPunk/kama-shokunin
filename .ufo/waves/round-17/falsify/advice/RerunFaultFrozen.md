VERDICT: confirm — C1's frozen before count reproduces: 5 detected / 3 accepted, with F5, F6, and F8 accepted as claimed.

## Scope
Attacked only the frozen/before fault-controls count from the round-17 claim. The claim is explicit at `corpus/lessons/round-17.md:157-159`: “frozen check.py … 5 detected, 3 accepted (F5 served_model, F6 route skip, F8 malformed), exit 1.”

## Results
I cloned the lane at `54a29268e2083caa2b1e0d54ee1e7d90961302f3` under `/tmp/KamaR17.RerunFaultFrozen-clone` and ran the requested command twice. Both runs returned detector exit 1 with 5 detected and 3 accepted. Full JSON comparison of rerun 2 against `.ufo/waves/round-17/runs/fault-controls-frozen.json`, excluding only wall-clock `seconds`, matched: schema, check/probe digests, matrix digest, F0, every fault field and full `why` strings, and totals. Recorded time 53.1 s; rerun 2 55.3 s.

Per-entry agreement (recorded vs rerun 2):

| Entry | Recorded → rerun `detected` | Recorded → rerun `check_exit` | Result |
|---|---|---|---|
| F0 positive control | true → true | 0 → 0 | agree |
| F1 reason forged | true → true | 1 → 1 | agree |
| F2 exit flipped | true → true | 1 → 1 | agree |
| F3 drift negated | true → true | 1 → 1 | agree |
| F4 verdict lower-cased | true → true | 1 → 1 | agree |
| F5 served_model forged | false → false | 0 → 0 | agree; accepted |
| F6 route skip | false → false | [0,0,0,0] → same | agree; accepted |
| F7 hang | true → true | 1 → 1 | agree |
| F8 malformed stdout | false → false | [1,1,1,1,1,1] → same | agree; accepted |

The recorded totals are `detected: 5`, `accepted: 3` (`runs/fault-controls-frozen.json:155-156`); fault entry IDs are at lines 86 (F5), 100 (F6), and 132 (F8). Thus 8/8 faults and F0 agree; F0 is separately reported as the positive control, not included in the 5+3 fault total.

Frozen-copy identity also checks out: `frozen/manifest.json:19-21` records the frozen `tests/probe-verdicts/check.py` copy and sha256 `b853576e…5762`; `sha256sum` of that copy and `git show cff9e62f05aa7cfb9059444f62eb787100719713:tests/probe-verdicts/check.py` produced the same digest. The run JSON's `check_sha256` is identical. The frozen manifest's source commit is `cff9e62…` (`manifest.json:3`).

## Fault-classification review
The detector's stated rule is at `tests/probe-verdicts/fault-controls.py:15-19`: detection requires exit 1 plus parseable JSON; anything else, including non-JSON/traceback output, is accepted. `classify_run` implements that distinction and requires the targeted conjunct (`:482-504`, and target check later in the function). This makes the F8 result consistent: the full recorded F8 `why` at `runs/fault-controls-frozen.json:152` shows the row-not-object, row-null, and non-utf8 variants exit 1 with non-parseable, empty stdout. They are accepted even though other variants yield JSON failure rows. That matches the claimed malformed-output gap (lesson `round-17.md:20-28` says the old check raised uncaught `AttributeError` and the repair records malformed/non-UTF-8 output per row).

The accepted mutations are substantive: F5 sets `served_model` to `kama-forged-id` (`fault-controls.py:292-293`); F6 skips `/v1/models` and replays cached output after `/health` (`:153-156`); F8 enumerates six malformed payloads, including non-UTF-8 bytes (`:167-187`). F0 is a positive-control gate against reject-everything (`:20-21`), and the matrix digest is pinned (`:74-76`).

## Exact commands and outcomes
Commands ran in the temporary clone; no lane gate or test was run in place.

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.RerunFaultFrozen-clone && git -C /tmp/KamaR17.RerunFaultFrozen-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3 && git -C /tmp/KamaR17.RerunFaultFrozen-clone log -1 --format='%H %ci %s'
# exit 0

PYTHONDONTWRITEBYTECODE=1 python3 tests/probe-verdicts/fault-controls.py --check .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --json; echo "EXIT=$?"
# detector exit 1; output: detected=5, accepted=3

PYTHONDONTWRITEBYTECODE=1 timeout 220 python3 tests/probe-verdicts/fault-controls.py --check .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --json > /tmp/KamaR17.RerunFaultFrozen-run2.json 2>/tmp/KamaR17.RerunFaultFrozen-run2.err; echo "EXIT2=$?"
# timeout-wrapped detector exit 1; output file: detected=5, accepted=3

git show cff9e62f05aa7cfb9059444f62eb787100719713:tests/probe-verdicts/check.py | sha256sum
# exit 0; digest b853576e…5762

sha256sum .ufo/waves/round-17/frozen/tests_probe-verdicts_check.py tests/probe-verdicts/check.py tests/probe-verdicts/fault-controls.py && git log --oneline -3 -- tests/probe-verdicts/fault-controls.py
# exit 0; frozen check digest b853576e…5762

python3 - <<'EOF'
import json
rec = json.load(open('.ufo/waves/round-17/runs/fault-controls-frozen.json'))
run2 = json.load(open('/tmp/KamaR17.RerunFaultFrozen-run2.json'))
keys = ['schema','check','check_sha256','probe_sha256','matrix']
for k in keys:
    print(f"{k}: {'MATCH' if rec.get(k)==run2.get(k) else 'DIFF'}")
def strip(d):
    d = json.loads(json.dumps(d)); d.pop('seconds',None); return d
print('top-minus-seconds:', 'MATCH' if strip(rec)==strip(run2) else 'DIFF')
print(f"seconds: recorded={rec['seconds']} run2={run2['seconds']}")
print(f"totals: recorded detected={rec['detected']} accepted={rec['accepted']} | run2 detected={run2['detected']} accepted={run2['accepted']}")
print('F0 positive:', 'MATCH' if rec['positive_control']==run2['positive_control'] else 'DIFF')
for a,b in zip(rec['faults'], run2['faults']):
    diffs=[k for k in a if a[k]!=b.get(k)]
    print(f"{a['id']}: detected rec={a['detected']} run2={b['detected']} exit rec={a['check_exit']} run2={b['check_exit']} -> {'AGREE' if not diffs else 'DIFF:'+','.join(diffs)}")
EOF
# exit 0; every compared field matched
```

## Limitations and residue
- Only the frozen/before count was in scope; I did not rerun the current/after count or mutant grid.
- Two reruns on the same host are reproducibility checks, not a distribution study; runtime varied while output did not.
- No tool was installed. No server was started; the wrapper uses loopback HTTP requests only.
- Removed my `/tmp/KamaR17.RerunFaultFrozen-*` clone and run-output scratch after collecting results.
