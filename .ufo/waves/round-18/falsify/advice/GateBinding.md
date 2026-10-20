# KamaR18.GateBinding — falsify: v3 gate `source_binding` validation

VERDICT: confirm — all eight independently mutated identity fields (url, path, commit, span_text, span_sha256, file_sha256, lines, row) plus three adversarial variants (host swap, consistent relocation, extra entry) are rejected by the delivered v3 gate with a problem naming the mutated field; the validator pins the full `tools/server/` URL (M6 bug shape now rejected); the gate performs internal-consistency/pinned-identity validation only and performs no upstream authentication — I verified the pins against upstream once, offline-to-online, and they hold.

Seat: KamaR18.GateBinding (leaf; no subagents dispatched). Attack target: `tests/llamacpp-live/check-receipt.py` v3 `source_binding` gate. Clone: `/tmp/kama-r18-falsify-GateBinding`, branch `seat/GateBinding` at `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` ("round-18: retain measured arms and repair counter classification seams", 2026-10-20 20:13:58 -0300). All commands ran inside the clone; the lane repo was only read for context files (lessons, SCORECARD §Round 18 at `SCORECARD.md:737-761`, `corpus/QUALITY.md:126-133` KQ23/KQ24). No lane writes, no `jj`/git writes anywhere, no official counting commands.

## Scope and claims attacked

- C1 v3 gate: "pinned source-binding validation" and M6's fix ("delivered gate and its synthetic receipts both dropped `tools/server/` from source-binding URLs; L1 corrected validator and synthetic builder to full pinned path") — `corpus/lessons/round-18.md` Mistakes table, M6 row.
- Assignment decomposition: (a) mutate each `source_binding` identity field independently and require a targeted rejection; (b) verify the full-URL pin specifically (the L1 integration bug shape); (c) distinguish what the gate actually validates (internal consistency / pinned identity) from upstream authentication (which it explicitly does not do), and check whether that boundary is honestly stated.

## Ground truth read before mutating

- `tests/llamacpp-live/check-receipt.py` (sha256 `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335`): `validate_source_binding` at `:113-158` compares every binding positionally against `SOURCE_BINDING_EXPECTED` (`:92-110`): eight equality-checked keys (`check`, `row`, `commit`, `path`, `url`, `lines`, `span_sha256`, `file_sha256`) plus re-derivation `sha256(span_text) == pinned span_sha256` (`:151`) and a line-count check `len(text.splitlines(keepends=True)) == lines[1]-lines[0]+1` against the pinned range (`:155`). Invocation is v3-gated: `:829-831` (`if is_v3:`; `is_v3` = `schema == "kama-llamacpp-live/v3"` at `:269`).
- The header states the boundary verbatim: "It never fetches upstream source: file digests are checked against the pinned identities and span hashes are re-derived from text" (`:8-10`); "the gate does not fetch or independently authenticate upstream file bytes" (`:88-91`). Verified: imports are `argparse copy datetime hashlib json os subprocess sys tempfile` (`:34-42`); the only `subprocess` uses are selftest re-invocations of the gate itself (`:2008-2011`, `:2028-2031`); no `urllib/requests/http.client/socket` anywhere in the file.
- Producer half: `tools/kama-llamacpp-live.py` (sha256 `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b`) `_binding` at `:902-914`, `source_bindings()` at `:925-997`, receipt attachment at `:1236`.
- Pinned constants: `LLAMA_COMMIT = 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`:79`), `LLAMA_RAW = https://raw.githubusercontent.com/ggml-org/llama.cpp/{commit}/` (`:80-87`); all five pinned `path` values carry the full `tools/server/` prefix (`:92-110`), and the expected `url` is derived as `LLAMA_RAW + path` (`:135`) — so a truncated URL cannot pass unless the path is also corrupted, and the path is itself pinned.

## Experiment (exact script, command, outputs)

Script: `seat-work/mutate_source_binding.py` (full source in Appendix A; 8.7 KB, written into the seat scratch clone). Invocation:

```
$ python3 /tmp/kama-r18-falsify-GateBinding/seat-work/mutate_source_binding.py
```

Baseline E0: byte-identical copy of the committed real v3 receipt `.ufo/waves/round-18/live/receipt-1.json` (sha256 `e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75`) → `check-receipt.py pristine.json --require-schema v3` → **exit 0, `VALID`**. The original receipt bytes were re-hashed after all runs: unchanged. Green pristine satisfied before every red mutation; every mutant is a fresh `deepcopy` written to a new file, so no restoration step was ever needed and byte-identity was proven at the end.

E1 three-way identity: `tools.kama-llamacpp-live.source_bindings() == receipt-1.json["source_binding"]` → `True`; each receipt entry equals the gate's `SOURCE_BINDING_EXPECTED`-derived expectation on all eight keys → `[]` mismatches.

### E3 mutation matrix — one field at a time (all runs exit 1, `INVALID ...`)

| # | Mutant (entry, field → value) | Gate problem observed | Killed |
|---|---|---|---|
| 01 | [0] `url` → M6 bug shape: `/tools/server/` dropped from URL | `source_binding[0].url 'https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d…/server-context.cpp' != pinned '…/tools/server/server-context.cpp'` | yes |
| 02 | [0] `url` → host `ggml-org`→`evil-org` | `source_binding[0].url … != pinned …` | yes |
| 03 | [0] `path` → `server-context.cpp` (URL left at pinned full value) | `source_binding[0].path 'server-context.cpp' != pinned 'tools/server/server-context.cpp'` (exactly 1 problem — no url problem exists because the untouched URL still equals the pinned derivation) | yes |
| 04 | [0] `commit` → `"0"*40` | `source_binding[0].commit '0000…' != pinned '704366d7…'` | yes |
| 05 | [0] `span_text` → one char flipped (`"ok"`→`"0k"` in the health body), span_sha left intact | `source_binding[0].span_text does not match the pinned span_sha256` | yes |
| 06 | [0] `span_sha256` → `"0"*64` | `source_binding[0].span_sha256 '0000…' != pinned '2ff50edd…'` | yes |
| 07 | [0] `file_sha256` → `"0"*64` | `source_binding[0].file_sha256 '0000…' != pinned 'dd1de0f2…'` | yes |
| 08 | [0] `lines` → `[5288, 5298]` | `source_binding[0].lines [5288, 5298] != pinned [5288, 5299]` | yes |
| 09 | [1] `row` → `"S999"` | `source_binding[1].row 'S999' != pinned 'S036'` | yes |
| 10 | [0] `check` → `"health_ignored"` | `source_binding[0].check 'health_ignored' != pinned 'health_ready'` | yes |
| 11 | [2] "internally-consistent relocation": entry 2 re-pointed at entry 3's span (span hash matches its own text, line count matches its own range) | 3 problems: `source_binding[2].lines [519, 523] != pinned [529, 534]`; `source_binding[2].span_sha256 '97408c51…' != pinned 'f14a9b67…'`; `span_text does not match the pinned span_sha256` | yes |
| 12 | append duplicate 6th entry | `source_binding has 6 entries, want exactly 5 pinned spans` | yes |

Note on 11: the only thing standing between a self-consistent forgery and acceptance is the pinned constant — i.e. the gate enforces **pinned identity**, not mere internal consistency. That is the stronger property, and it is what makes upstream authentication unnecessary *given* honest constants (checked below).

Additional type-confusion probes (same harness, `tc-*.json`, all exit 1): `lines=[True, 5299]` → `… != pinned [5288, 5299]`; `row=False` (vs pinned `None`) → `source_binding[0].row False != pinned None`; `row=36` (vs `"S036"`) → `… 36 != pinned 'S036'`; CRLF-injected `span_text` → hash mismatch. No bool/int equality escape exists against these pinned values.

## (b) Full tools/server URL (the M6 L1 integration bug)

- The historical bug shape — receipt and synthetic builder both emitting `…/{commit}/server-context.cpp` without `tools/server/` — is now rejected on the real-receipt path: mutant 01 (exit 1, problem above). The gate cannot be fed the M6 shape as `url` alone.
- The delivered synthetic builder `_selftest_source_binding` (`:1395-1465`) builds `url = LLAMA_RAW + path` with full pinned paths, so the selftest can no longer mask a truncated-URL validator (the round-17 hiding mechanism was the synthetic receipt and validator agreeing on the truncated shape; both now derive from the same full pinned path tuple).
- Delivered selftest: `check-receipt.py --selftest` → exit 0, `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`. Its source-binding mutant set is exactly one: `v3-source-binding-tampered` (`:1911-1912`, `row="S999"` on entry 0). Mutants 01-12 above are fresh attacks outside that denominator and none survived.

## (c) Internal consistency vs upstream authentication

What the gate validates (all offline, no network): field-by-field pinned equality + `sha256(span_text)` + line-count vs pinned range. What it cannot validate: that the pinned constants themselves correspond to the real upstream bytes at that commit, and that `span_text` really sits at those line numbers in that file (it has no file bytes; the line-count check is size-only). The header discloses exactly this (`:8-10`, `:88-91`); the disclosure is accurate, not an overclaim.

I closed the authentication gap once, from the seat, so the residual is "constants could drift between releases of this repo", not "constants were never authentic":

- Fresh HTTPS fetch, `curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path> | sha256sum`, all three files match the gate's pinned `file_sha256` exactly:
  - `tools/server/server-context.cpp` → `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`
  - `tools/server/server-http.cpp` → `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`
  - `tools/server/server.cpp` → `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`
- Offline span/line authentication against the round-17 pinned copies in the clone (`.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`): for each of the five bindings, the extracted 1-based slice `lines[a-1:b]` of the pinned file equals the receipt `span_text` byte-for-byte, its sha256 equals the pinned `span_sha256`, and the whole-file digest equals the pinned `file_sha256` — `E2 OK` (5/5 MATCH, script output above). So the line anchors are real, not just self-consistent; this goes beyond the gate's size-only line check.

## Boundary findings (not defects against the declared contract, recorded for L1)

1. **v3-only enforcement is by design but worth keeping visible.** `validate_source_binding` runs only under `is_v3` (`:829`). Demonstrated: the committed round-17 v2 receipt `.ufo/waves/round-17/live/receipt-1.json` (sha256 `f34afb545db28fc37b2df8179f5872d2e84a20a140a0f3367a9f60d1864702a4`) with the same truncated-URL mutation applied to its `source_binding[0]` still exits **0 VALID** (v2 pristine also VALID). The v2 historical path keeps its round-17 behavior (no source-binding obligation — round-17 finding `SourceBindingCheck.md` accepted this for v2). Round-18's claim is about the v3 gate, so this is a scope statement, not a kill.
2. **Extra keys on a binding are tolerated** (`binding.get(key)` equality only; an unexpected 9th key raises no problem). Harmless: every identity field is still pinned; noted so nobody mistakes the validator for a schema-closed object check.
3. **Gate selftest covers one source-binding mutant only** (`row` corruption). The fresh matrix above shows the validator itself rejects the other seven identity fields; if the wave wants selftest-parity for every field, that is new surface, not a hole — the gate's own declared bar ("reject changed identities") is met and exceeded by the validator code.

## KQ23/KQ24 framing

- KQ23 (control-path overclaims): the M6 fix claim is now supported by executed evidence, not citation alone — the exact bug shape was re-created as a mutant and rejected at pinned bytes (`SOURCE_BINDING_EXPECTED:92-110`, mutant 01).
- KQ24 (not-evaluated vs failed): my scope found no laundering path through `source_binding`; the field carries no tri-state semantics (`row: null` is a registry-provenance marker, not an evaluation outcome — `tools/kama-llamacpp-live.py:895-898`).

## Residual risk / verification gaps

- The gate's `file_sha256`/`span_sha256`/line constants are only as honest as the gate file itself; an attacker who controls the gate source controls the pins. My upstream cross-check binds today's constants to upstream bytes and today's pinned copies, not future revisions. This matches the gate's own stated limitation — no discrepancy found.
- The line-count check is size-only by construction; my E2 run supplied the content-anchoring the gate cannot (span == exact pinned-file slice, 5/5).
- One cosmetic script artifact: my harness labeled mutant 03 "SURVIVED" because it demanded a *second* url problem that cannot exist (mutating `path` alone leaves the pinned `url` still correct). The gate's observed behavior is correct (exit 1, exactly the `path` problem); the label was my assertion bug, corrected in the table above. All 16 executed v3-receipt mutants (12 matrix + 4 type-confusion) were rejected; zero survived. The v2-boundary mutant was accepted by contract (finding B1) and the delivered selftest additionally rejected its 61 internal mutants.
- No tool installs were needed (python 3.14.8 and curl 8.23.0 already present; no pacman/uv/npm usage).

## Cleanup (executed)

- Seat processes: `pgrep -af 'seat-work'` → no output (exit 1); `pgrep -af 'kama-r18-falsify-GateBinding'` → no output (exit 1); `ss -ltnp | grep -E '8080|34113'` → no output (exit 1). No seat-owned listener exists; the experiments spawn no servers (gate is offline validation only).
- Scratch clone `/tmp/kama-r18-falsify-GateBinding` (including `seat-work/` and all mutant JSON files) removed after this report was written; nothing copied back except this report and the experiment source embedded in Appendix A.

## Appendix A — exact experiment source

`seat-work/mutate_source_binding.py` as executed (byte-for-byte; the only post-run change was the harness label fix described above, which lives in my report table, not in the file that ran):

```python
#!/usr/bin/env python3
"""KamaR18.GateBinding — independent source_binding mutation attack.

Clone: /tmp/kama-r18-falsify-GateBinding @ 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
Baseline: committed .ufo/waves/round-18/live/receipt-1.json (never modified;
every mutant is a fresh in-memory deepcopy written to seat-work/).
"""
import copy
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import sys

REPO = pathlib.Path("/tmp/kama-r18-falsify-GateBinding")
GATE = REPO / "tests/llamacpp-live/check-receipt.py"
TOOL = REPO / "tools/kama-llamacpp-live.py"
RECEIPT_V3 = REPO / ".ufo/waves/round-18/live/receipt-1.json"
RECEIPT_V2 = REPO / ".ufo/waves/round-17/live/receipt-1.json"
PINNED = REPO / ".ufo/waves/round-17/sources/llama.cpp-704366d76"
WORK = REPO / "seat-work"
WORK.mkdir(exist_ok=True)

PRISTINE_SHA = hashlib.sha256(RECEIPT_V3.read_bytes()).hexdigest()
print(f"pristine receipt sha256: {PRISTINE_SHA}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = load("gate_mod", GATE)
tool = load("tool_mod", TOOL)


def run_gate(receipt_path, *extra):
    proc = subprocess.run(
        [sys.executable, str(GATE), str(receipt_path), *extra],
        capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


verdicts = []


def expect_kill(name, receipt_obj, want_substrings, *extra):
    path = WORK / f"mut-{name}.json"
    path.write_text(json.dumps(receipt_obj, indent=2, sort_keys=True) + "\n")
    rc, out, err = run_gate(path, *extra)
    first = out.strip().splitlines()[0] if out.strip() else ""
    hit = [s for s in want_substrings if s in out]
    ok = rc == 1 and len(hit) == len(want_substrings)
    verdicts.append(ok)
    print(f"{'KILLED ' if ok else 'SURVIVED'} {name}: exit={rc} verdict={first!r}")
    for line in out.strip().splitlines()[1:]:
        print(f"    {line}")
    if err.strip():
        print(f"    stderr: {err.strip()[:200]}")
    return ok


# E0 — pristine baseline must be green on a byte-identical copy
pristine = WORK / "pristine.json"
shutil.copyfile(RECEIPT_V3, pristine)
assert hashlib.sha256(pristine.read_bytes()).hexdigest() == PRISTINE_SHA
rc, out, err = run_gate(pristine, "--require-schema", "v3")
print(f"E0 pristine: exit={rc} {out.strip().splitlines()[0] if out.strip() else ''!r}")
assert rc == 0 and out.startswith("VALID"), (rc, out, err)
print("E0 OK\n")

# E1 — producer / committed receipt / gate constants three-way equality
bind_prod = tool.source_bindings()
base = json.loads(RECEIPT_V3.read_text())
bind_receipt = base["source_binding"]
print("E1 producer source_bindings() == receipt source_binding:",
      bind_prod == bind_receipt)
const_problems = []
for i, (check, row, path, lines, fsha, ssha) in enumerate(
        gate.SOURCE_BINDING_EXPECTED):
    exp = {"check": check, "row": row, "commit": gate.LLAMA_COMMIT,
           "path": path, "url": gate.LLAMA_RAW + path,
           "lines": list(lines), "file_sha256": fsha, "span_sha256": ssha}
    for key, val in exp.items():
        if bind_receipt[i].get(key) != val:
            const_problems.append((i, key, bind_receipt[i].get(key), val))
print("E1 gate SOURCE_BINDING_EXPECTED vs receipt mismatches:", const_problems)
assert bind_prod == bind_receipt and not const_problems
print("E1 OK\n")

# E2 — offline authentication against the in-repo pinned upstream bytes
print("E2 pinned-copy verification (gate itself cannot do this):")
for i, b in enumerate(bind_receipt):
    f = PINNED / b["path"]
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    src_lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
    span = "".join(src_lines[b["lines"][0] - 1:b["lines"][1]])
    span_ok = span == b["span_text"]
    span_d = hashlib.sha256(span.encode()).hexdigest()
    print(f"  [{i}] {b['path']} {b['lines']}: file_sha "
          f"{'MATCH' if digest == b['file_sha256'] else 'MISMATCH ' + digest}; "
          f"span==lines {'MATCH' if span_ok else 'MISMATCH'}; span_sha "
          f"{'MATCH' if span_d == b['span_sha256'] else 'MISMATCH ' + span_d}")
    assert digest == b["file_sha256"] and span_ok and span_d == b["span_sha256"]
print("E2 OK\n")

# E3 — mutation matrix: one field at a time
def mutated(fn, idx=0):
    r = copy.deepcopy(base)
    fn(r["source_binding"][idx], r)
    return r


def set_key(key, value):
    def fn(b, _r):
        b[key] = value
    return fn


# 1 url: the exact M6 integration-bug shape (tools/server/ dropped)
expect_kill("01-url-truncated",
            mutated(lambda b, r: b.update(
                url=r and b["url"].replace("/tools/server/", "/"))),
            ["source_binding[0].url"])
# 2 url: wrong host
expect_kill("02-url-evil-host",
            mutated(lambda b, r: b.update(
                url=b["url"].replace("ggml-org", "evil-org"))),
            ["source_binding[0].url"])
# 3 path truncated (url left at pinned full value)
expect_kill("03-path-truncated",
            mutated(set_key("path", "server-context.cpp")),
            ["source_binding[0].path", "source_binding[0].url"])
# 4 commit zeroed
expect_kill("04-commit-zeroed",
            mutated(set_key("commit", "0" * 40)),
            ["source_binding[0].commit"])
# 5 span_text one-char flip, span_sha256 left untouched
def flip_char(b, _r):
    b["span_text"] = b["span_text"].replace('{"status", "ok"}',
                                            '{"status", "0k"}', 1)
expect_kill("05-span-text-flip", mutated(flip_char),
            ["source_binding[0].span_text does not match"])
# 6 span_sha256 zeroed
expect_kill("06-span-sha-zeroed", mutated(set_key("span_sha256", "0" * 64)),
            ["source_binding[0].span_sha256"])
# 7 file_sha256 zeroed
expect_kill("07-file-sha-zeroed", mutated(set_key("file_sha256", "0" * 64)),
            ["source_binding[0].file_sha256"])
# 8 line range shrunk
expect_kill("08-lines-shrunk", mutated(set_key("lines", [5288, 5298])),
            ["source_binding[0].lines"])
# 9 row corrupted on entry 1 (S036 -> S999)
expect_kill("09-row-s999", mutated(set_key("row", "S999"), idx=1),
            ["source_binding[1].row"])
# 10 check renamed on entry 0
expect_kill("10-check-renamed", mutated(set_key("check", "health_ignored")),
            ["source_binding[0].check"])
# 11 internally-consistent relocation: entry 2 re-points at entry 3's span;
# span hash matches its text, count matches its lines — only the pinned
# constants stand between this forgery and acceptance.
def relocate(b, _r):
    donor = copy.deepcopy(base["source_binding"][3])
    b["lines"] = donor["lines"]
    b["span_text"] = donor["span_text"]
    b["span_sha256"] = donor["span_sha256"]
expect_kill("11-consistent-relocation", mutated(relocate, idx=2),
            ["source_binding[2].lines", "source_binding[2].span_sha256"])
# 12 extra sixth entry appended
def append_dup(b, r):
    r["source_binding"].append(copy.deepcopy(r["source_binding"][4]))
expect_kill("12-extra-entry", mutated(append_dup),
            ["source_binding has 6 entries"])

# E4 — v2 boundary: same corruption on a v2 receipt is NOT gated (by contract)
v2 = json.loads(RECEIPT_V2.read_text())
assert v2["schema"] == "kama-llamacpp-live/v2"
v2_pristine = WORK / "v2-pristine.json"
v2_pristine.write_text(json.dumps(v2))
rc, out, _ = run_gate(v2_pristine)
print(f"\nE4 v2 pristine: exit={rc} {out.strip().splitlines()[0]!r}")
v2mut = copy.deepcopy(v2)
v2mut["source_binding"][0]["url"] = v2mut["source_binding"][0][
    "url"].replace("/tools/server/", "/")
v2_mut = WORK / "v2-mut-url.json"
v2_mut.write_text(json.dumps(v2mut))
rc2, out2, _ = run_gate(v2_mut)
first2 = out2.strip().splitlines()[0] if out2.strip() else ""
print(f"E4 v2 url-truncated mutant: exit={rc2} {first2!r}")
verdicts.append(rc == 0)
print(f"E4 boundary confirmed (v2 mutant {'ACCEPTED' if rc2 == 0 else 'rejected'})")

# E5 — delivered gate selftest (includes v3-source-binding-tampered mutant)
rc, out, err = run_gate(WORK / "selftest-placeholder", "--selftest")
print(f"\nE5 gate --selftest: exit={rc}")
print("\n".join(out.strip().splitlines()[-3:]))
verdicts.append(rc == 0 and "source-binding-tampered" not in err)

# Final integrity: pristine byte-identity never disturbed
assert hashlib.sha256(RECEIPT_V3.read_bytes()).hexdigest() == PRISTINE_SHA
assert hashlib.sha256(pristine.read_bytes()).hexdigest() == PRISTINE_SHA
print(f"\npristine receipt still byte-identical: sha256 {PRISTINE_SHA}")
print(f"RESULT: {sum(verdicts)}/{len(verdicts)} expectations met")
sys.exit(0 if all(verdicts) else 1)
```

Upstream-authentication command as executed:

```
$ cd /tmp/kama-r18-falsify-GateBinding && for f in tools/server/server-context.cpp tools/server/server-http.cpp tools/server/server.cpp; do printf '%s  ' "$f"; curl -fsSL --max-time 60 "https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/$f" | sha256sum; done
tools/server/server-context.cpp  dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329  -
tools/server/server-http.cpp  24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb  -
tools/server/server.cpp  2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4  -
```

Type-confusion probe harness (executed inline after the main script):

```python
import copy, json, subprocess, sys, pathlib
REPO = pathlib.Path('/tmp/kama-r18-falsify-GateBinding')
GATE = REPO / 'tests/llamacpp-live/check-receipt.py'
base = json.loads((REPO/'.ufo/waves/round-18/live/receipt-1.json').read_text())
def run(name, obj):
    p = pathlib.Path(f'tc-{name}.json'); p.write_text(json.dumps(obj))
    r = subprocess.run([sys.executable, str(GATE), str(p)], capture_output=True, text=True)
    ...
# cases: lines=[True,5299]; row=False; row=36; span_text CRLF injection — all exit 1 with the named field problem
```
