VERDICT: partial — the 0→79 spawn fix and policy/hash receipts validate, but refused attempts are still undercounted.

## Findings

### Medium — refusal records report zero for 82 refused tasks

The round-17 build ledger records the `refused` attempt as parseable with `refused: 0` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/provenance-ledger.json:5-25`, quote: `"label": "refused" ... "refused": 0`). Its input is not refusal-free: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/refused-result-1.json:4` contains task-specific `Background job limit reached (100)` errors; a count over that payload found 82 messages and 82 unique task IDs. The dispatch reports 82 tasks (`.../build/dispatch.json:16-19`). Re-running the round-17 tool against a scratch copy of the ledger and this payload again appended `parseable: true, refused: 0` (exit 0). The extractor only tallies integer `refused`/`spawned` fields and exact `status`/`state` values (`.../round-17/dispatch-provenance.py:365-384`, quote: `if key in ("refused", "spawned") and isinstance(value, int)`); it does not classify refusal messages in `result.text`. Thus the recorded refusal count is not a faithful count of this attempt.

## Confirmed checks

- Re-ran the 0→79 demo in a clone of commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, using separate copies of the round-16 falsify ledger. The round-16 script exited 0 and recorded `spawned: 0`; the round-17 script exited 0 and recorded `spawned: 79` via `omp_text_spawned_header`. This matches the committed demo (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/provenance-0to79-demo.txt:1-6`).
- The pinned build validation includes policy `path`, `sha256`, `version: v2`, and `band` (`.../round-17/build/validation.json:38-46`) and records the single canonicalization (`.../validation.json:18-19`). `sha256sum` of the policy file matched the recorded `70418a0f…a64f59f9` digest.
- Recomputed SHA-256 over `build/dispatch.json`'s `taskCall` using the recorded sorted-key, tight-separator, `ensure_ascii=False` UTF-8 canonicalization: `70e994a07cad5e86d6aaa34c6a62eb6ff0f1542ac0bb02ef2f4ca0d184c8fb4f`, matching `validation.json:18`; the dispatch has 82 tasks (`dispatch.json:528-530`).

## Residual risk

Refused results represented only as free-form text remain invisible to the current refused counter; the demonstrated 82-task failure is persisted as zero.

## Verification gaps

No `lsp` device/server is exposed in the mounted tool inventory, so LSP status, references, definitions, and diagnostics were unavailable. This review was limited to the pinned provenance artifacts, targeted source reads, and the requested scratch reruns; no full test suite was run. No tools were installed or updated.

## Commands and results

```text
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.ProvenanceRerun-clone && git -C /tmp/KamaR17.ProvenanceRerun-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
exit 0

(cd /tmp/KamaR17.ProvenanceRerun-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-16/dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json --label spawned --out /tmp/KamaR17.ProvenanceRerun-run/r16-old-ledger.json)
exit 0; result: spawned=0

(cd /tmp/KamaR17.ProvenanceRerun-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/dispatch-provenance.py --attempt-result .ufo/waves/round-16/falsify/spawn-result.json --label spawned --out /tmp/KamaR17.ProvenanceRerun-run/r16-new-ledger.json)
exit 0; result: spawned=79

PYTHONDONTWRITEBYTECODE=1 python3 -c 'import hashlib,json; from pathlib import Path; root=Path("/tmp/KamaR17.ProvenanceRerun-clone/.ufo/waves/round-17/build"); d=json.loads((root/"dispatch.json").read_text()); v=json.loads((root/"validation.json").read_text()); b=json.dumps(d["taskCall"],sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8"); actual=hashlib.sha256(b).hexdigest(); print("recomputed="+actual); print("recorded="+v["taskCall_sha256"]); print("match="+str(actual==v["taskCall_sha256"])); print("tasks="+str(len(d["taskCall"]["tasks"]))); print("validation_policy="+json.dumps(v["policy"],sort_keys=True,separators=(",",":"))); print("canonicalization="+v["canonicalization"])'
exit 0; match=True; tasks=82

sha256sum /home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json
exit 0; digest matched validation.json

(cd /tmp/KamaR17.ProvenanceRerun-clone && PYTHONDONTWRITEBYTECODE=1 python3 .ufo/waves/round-17/dispatch-provenance.py --attempt-result .ufo/waves/round-17/build/refused-result-1.json --label refused --out /tmp/KamaR17.ProvenanceRerun-run/refusal-ledger.json)
exit 0; appended refused=0

PYTHONDONTWRITEBYTECODE=1 python3 -c 'import json,re,sys; from pathlib import Path; p=Path("/tmp/KamaR17.ProvenanceRerun-clone/.ufo/waves/round-17/build/refused-result-1.json"); payload=json.loads(p.read_text()); text=payload["result"]["text"]; ids=re.findall(r"(KamaR17\.[\w-]+): Background job limit reached",text); ledger=json.loads(Path("/tmp/KamaR17.ProvenanceRerun-run/refusal-ledger.json").read_text()); last=ledger["entries"][-1]; print("textual_refusal_messages="+str(text.count("Background job limit reached"))); print("unique_task_ids="+str(len(set(ids)))); print("appended="+json.dumps({k:last.get(k) for k in ("label","parseable","refused","spawned","bound_task_call_sha256")},sort_keys=True)); assert len(ids)==82 and len(set(ids))==82 and last["refused"]==0'
exit 0; textual messages=82, unique IDs=82, appended refused=0

rm -rf -- /tmp/KamaR17.ProvenanceRerun-clone /tmp/KamaR17.ProvenanceRerun-run
exit 0; both scratch directories absent
```
