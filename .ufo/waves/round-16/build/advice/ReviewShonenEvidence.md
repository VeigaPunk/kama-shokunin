# ReviewShonenEvidence — C2 live receipt and SHONEN box 2

**Seat:** `KamaR16.ReviewShonenEvidence` (leaf, read-only). **Lane:** kama-shokunin,
round 16 build wave. **Axes in scope:** operability 8 + calibration 7 (calibration is the
lowest assigned axis), so this is a calibration/evidence-wording review, not a measurement.

**Method:** read `SHONEN.md`, `PROTOCOL.md` (promotion gates, evidence standard, canonical
form), `LOG.md`, `PROVINCE.md`, `SKILL.md`, the round-16 build spec, the consumer registry,
and git state. No lane gate, harness, probe or test was executed by this seat; nothing was
written except this report. **Installs:** none.

---

## 1. Direct answer

A committed `kama-llamacpp-live/v1` receipt, cited by a `LOG.md` round-16 entry written as
**trigger → action → outcome → pointer**, lets box 2 honestly claim exactly one new thing:

> One **live, lane-owned, ephemeral llama.cpp endpoint task was executed end-to-end**: a
> pinned `llama-server` b11755 loaded a pinned GGUF on a non-consumer loopback port; the
> documented readiness/identity surfaces were captured; `kama-probe.sh` returned
> `MODEL_OK` / `matched` exit 0 with the real alias and `MODEL_MISMATCH` /
> `served-id-mismatch` exit 2 with a wrong expectation against the same live server; the
> server was torn down and the port proven closed. The run is logged in `LOG.md` §round 16
> and its receipt is committed in the repo.

That is the whole claim. It is fresher and receipt-backed relative to the present
pointer, which rests on `LOG.md` §§round 1–3 (`SHONEN.md:8`) and is stale relative to the current
`DEAD` registry state (`LOG.md:238`, `LOG.md:367`) and round 15's own statement that the
offline repair "is not a fresh serving-runtime task"
(`../.ufo/reports/round-15/kama.md:121`; also `LOG.md:903`, "No live endpoint/probe,").

### Box 2 must **not** claim

1. **Registered-consumer reconciliation or endpoint recovery.** The receipt grades a
   lane-started server; every registry row remains `DEAD` (registry/endpoint-consumers.tsv:35-37,
   "sampled DEAD in registry/history/latest.tsv"; `PROVINCE.md:24-25`, "Serving runtime is
   explicitly unavailable on the concrete surfaces"). Consumer repair stays operator-owned
   (`PROVINCE.md:45-46`, "kama never writes to `~/.config`, `~/.omp`, or systemd units").
2. **Other runtimes or other llama.cpp builds.** The receipt pins one build (b11755) and
   one tiny GGUF; it is not evidence for Ollama, vLLM, SGLang, TGI, LM Studio, KoboldCpp or
   a different llama.cpp release.
3. **Live loading enumeration or live `MODEL_LOADING` grading.** The schema records
   `loading_observed`, but the C2 contract says "observed or not-observed is recorded,
   never required" (`.ufo/waves/round-16/build/spec.json:59`); `true` shows the server
   emitted the loading body, n=1. The harness runs the probe only after `/health` is 200
   (`tools/kama-llamacpp-live.py:693`, `:742`), so it never grades the 503 live; C1's
   stub matrix remains the loading-verdict evidence.
4. **Generation or model quality.** The nine checks assembled at
   `tools/kama-llamacpp-live.py:709-786` cover metadata/readiness surfaces plus
   probe verdicts; there is no completion request. "Served the model" is defensible only as
   "loaded and identified", never as inference quality.
5. **Independent verification.** The receipt validator is lane-authored (`tests/llamacpp-live/check-receipt.py:352`,
   `.ufo/waves/round-16/build/spec.json:64`); it is intended to re-derive probe claims, but
   as currently written it looks for `json`/`started`/`port_closed` while the harness writes
   `result`/`started_utc`/`port_refuses` (F1a), so a green run is reported INVALID. Either
   way it is same-lane evidence: "Self-test green is capability, not a measurement"
   (`PROTOCOL.md:403`).
6. **That a lane-owned control instance settles the "domain's actual surfaces" reading.**
   The task touches a real runtime surface (`SKILL.md:18-19`, "Local model-serving processes
   and the ports they own (`llama-server` here)"), but whether a lane-started instance
   satisfies `PROTOCOL.md:361-362` ("one real work item executed against the domain's actual
   surfaces") is a **non-author** judgment. The receipt proves the execution; it cannot
   prove the reviewer's interpretation. It can, however, rule out a proven stranger: the
   receipt records `port_listener_ownership` and refuses readiness on `foreign`
   (`tools/kama-llamacpp-live.py:695-699`); a green receipt is `child` or `unknown`, never
   `foreign`, so `unknown` remains an explicit limit. **[INFERENCE]**

---

## 2. Replacement pointer text

Replace `SHONEN.md:8`. Keep the box line (`SHONEN.md:7`) byte-identical, keep the mark
`[~]`, and keep everything on **one** indented evidence line: the canonical form allows
"the box character plus one indented evidence line per box" and "no other prose, added
boxes" (`PROTOCOL.md:446`). Fill the angle-bracket values from the committed receipt; do not
paste predicted values.

```
      → Author assertion: `LOG.md` §round 16 (trigger→action→outcome→pointer) + `.ufo/waves/round-16/llamacpp-live-receipt.json` in the round commit: `<N>/9` `kama-llamacpp-live/v1` checks from one live pinned llama.cpp b11755 run on a pinned GGUF and an ephemeral non-consumer loopback port (`MODEL_OK`/`matched` exit 0, `MODEL_MISMATCH`/`served-id-mismatch` exit 2, teardown proven, `loading_observed`=`<true|false>`) — a lane-owned control, not registered-consumer reconciliation, other runtimes, generation or model quality; no non-author `[x]`.
```

Fill rules:

- `<N>/9`: the literal passed/total from the receipt's `checks` array, and the harness exit
  code must agree (exit 0 iff all pass, per `.ufo/waves/round-16/build/spec.json:59`). A red run uses
  the variant below; it must not wear the green sentence.
- `loading_observed`: `true` only if the receipt recorded a loading-503; else `false`. Do not
  upgrade this to a `MODEL_LOADING` live-coverage claim.
- Receipt path: use the **actual committed path**. `.ufo/waves/round-16/` is currently
  untracked (`git status --porcelain=v1` → `?? .ufo/waves/round-16/`); `.gitignore` excludes
  only `.ufo/interactive-sessions/` (`.gitignore:1`), so the receipt is committable but is
  not evidence until added. Never cite stdout, `/tmp`, or a session artifact —
  `PROTOCOL.md:369-370` requires the pointer to resolve at closure.
- Keep "§round 16" only once the LOG heading exists. Cite the heading text if L1 names it
  (e.g. `LOG.md` §round 16 — live llama.cpp endpoint task) so the pointer is unique.
- Do not add "receipt validated" or a validator exit `0` unless
  `tests/llamacpp-live/check-receipt.py` actually exits 0 on the committed receipt; as
  currently written, F1a predicts INVALID on a green harness receipt.

Red-run variant (execution remains loggable task evidence; the capability and the box do
not move) **[INFERENCE]**:

```
      → Author assertion: `LOG.md` §round 16 (trigger→action→outcome→pointer) + `.ufo/waves/round-16/llamacpp-live-receipt.json` in the round commit: one live pinned llama.cpp b11755 run executed (`<N>/9` checks, harness exit `<1>`; failing `<ids>`) on an ephemeral non-consumer loopback port — task logged, capability not demonstrated; a lane-owned control, not consumer reconciliation or other runtimes; no non-author `[x]`.
```

Exit `2` (setup failure) or `3` (server/model digest mismatch before launch) does not
produce a probed endpoint task: record the failure in the LOG, do not cite that receipt as
box-2 execution evidence, and leave the previous pointer in place. **[INFERENCE]**

Do **not** write `[x]` in this round from any build seat. Only a non-author may replace
`[~]` with `[x] <verifier-id>`: "Every `SHONEN.md` box checked by a reviewer who did not
author the round's changes" and "a subagent the lane dispatched is still the lane"
(`PROTOCOL.md:63-64`, `PROTOCOL.md:64-65`); "`[x]` only with a named non-author verifier"
(`PROTOCOL.md:464`). This review seat is a lane-dispatched subagent, so it also cannot
supply the `[x]`.

---

## 3. The `LOG.md` entry box 2 needs for the "logged" half

`PROTOCOL.md:361-362` requires the task be logged as trigger → action → outcome → pointer.
A LOG entry that only says "C2 measurement 9/9" does not meet that shape. Minimum skeleton:

```text
## round 16 — live llama.cpp endpoint task and receipt (2026-10-20)

- Trigger: box-2 evidence is historical only (`LOG.md` rounds 1–3); round 15 records
  "No live endpoint/probe," (`LOG.md:903`) and its report calls the offline repair
  "not a fresh serving-runtime task" (`../.ufo/reports/round-15/kama.md:121`).
- Action: `python3 tools/kama-llamacpp-live.py --server <realpath> --model <path>
  --model-sha256 <hex> --alias kama-live-probe --out .ufo/waves/round-16/llamacpp-live-receipt.json`
  (server b11755 / commit 704366d76 / asset sha256 753b…e226; model `stories260K.gguf`
  sha256 270c…256d; port `<P>`, not 8080/34113 nor any registry row).
- Outcome: harness exit `<0>`; receipt `kama-llamacpp-live/v1` `<N>/9` checks;
  probe `MODEL_OK`/`matched` exit 0 and `MODEL_MISMATCH`/`served-id-mismatch` exit 2;
  `/metrics` `<501>` without `--metrics`; `loading_observed`=`<bool>`; teardown: process
  exited and port closed. `python3 tests/llamacpp-live/check-receipt.py <receipt>
  --expect-model-sha256 <hex> --expect-server-sha256 <hex>`: record the actual exit;
  as currently written, F1a predicts INVALID from field-name drift, not from a failed run
  (lane validator, not independent).
- Pointer: `.ufo/waves/round-16/llamacpp-live-receipt.json` (committed with this round's
  commit; hash carried in the lane report).
```

Notes for L1:

- The receipt must be from **L1's measurement run**, not the C2 author's development run:
  the item text permits dev runs but says "such runs are not measurements"
  (`.ufo/waves/round-16/build/spec.json:59`). "Claimed ≠ re-executed" (`PROTOCOL.md:374`).
- Verify the receipt's port is absent from the registry at closure. The validator checks
  only the two literals 8080/34113 (`tests/llamacpp-live/check-receipt.py:33`,
  `FORBIDDEN_PORTS = {8080, 34113}`; `.ufo/waves/round-16/build/spec.json:64`, "port not
  8080/34113"); today the registry's only ports are those two
  (`registry/endpoint-consumers.tsv:35-37`), so a one-line `grep -w <P>
  registry/endpoint-consumers.tsv` (no output) makes the "non-consumer" wording
  re-derivable.
- Do not hand-edit the receipt's `started_utc`/`ended_utc`; the evidence timestamp must be
  at or before the shipping commit (`PROTOCOL.md:371-372`). Write the LOG entry and the
  SHONEN line after the run, and commit the receipt in the same round commit (or earlier
  than the review).
- `loading_observed=true` is a live observation, not C1 evidence; keep the C1 stub matrix
  as the calibration evidence and do not let one live request inflate the envelope claim.

---

## 4. What must remain `[~]`

1. **The mark itself.** The C2 receipt, the validator exit 0, and this report are all
   lane-side evidence. Box 2 stays `[~]` with a resolvable pointer until a named non-author
   reviews it (`PROTOCOL.md:63-67`).
2. **The "logged" half until the LOG entry exists.** A SHONEN pointer citing a LOG section
   that has not been written is unresolvable at closure (`PROTOCOL.md:369-370`); sequence
   receipt → LOG entry → SHONEN line → commit.
3. **The scope sentence in the pointer.** Consumer reconciliation, other runtimes/builds,
   live loading coverage (unless recorded), generation, and model quality all remain
   outside the receipt. The old caveat "current `DEAD` is not model readiness"
   (`SHONEN.md:8`) stays true; the replacement preserves it as the consumer/reconciliation
   exclusion.
4. **The interpretation that a lane-owned control is a "domain actual surface" for box 2.**
   Only a non-author can rule that; if the reviewer expects a field consumer path, the box
   remains `[~]` and the task is still a capability-integration run, not a promotion
   credential. **[INFERENCE]**
5. **Every other box.** Boxes 1, 3 and 4 are untouched by C2; this round does not enable a
   promotion and no `[x]` may appear on them from lane-side evidence.

---

## 5. Findings, severity ordered

### F1 — High — an uncommitted receipt is not evidence

`git status --porcelain=v1` currently shows `?? .ufo/waves/round-16/`; `.gitignore:1` ignores
only `.ufo/interactive-sessions/`. `PROTOCOL.md:369-370`: "An evidence pointer must resolve
at *closure* time, not only at write time". The pointer must name the receipt path that is
in the round commit, and L1 should confirm it after staging with
`git cat-file -e HEAD:<path>` (or the round commit's path) before filing the report. A
path-only local run or stdout pointer fails.

### F1a — High — the validator and harness do not share a receipt contract

Code inspection shows the two C2 artifacts do not share a field contract, so a green
`kama-llamacpp-live` run will still be reported `INVALID` by `check-receipt.py`:

- Timestamps: the harness writes `'started_utc'`/`'ended_utc'`
  (`tools/kama-llamacpp-live.py:624`, `:625`, `:790`), while the validator reads
  `receipt.get("started")`/`receipt.get("ended")`
  (`tests/llamacpp-live/check-receipt.py:356-357`, "is not a parseable ISO
  timestamp").
- Probe payload: the harness stores the parsed probe JSON under `result`
  (`tools/kama-llamacpp-live.py:466`, `rec['result'] = json.loads(cp.stdout)`), while the
  validator only reads `p.get("json")` (`tests/llamacpp-live/check-receipt.py:159`), so it
  finds no `MODEL_OK`/`MODEL_MISMATCH` rows and reports both probe checks missing.
- Teardown: the harness records `port_refuses`
  (`tools/kama-llamacpp-live.py:516`, `out['port_refuses'] = True`) and the check observes
  `{"port_refuses": ...}` (`:784-785`), while the validator looks for `port_closed`,
  `port_refused`, `port_dead` (`tests/llamacpp-live/check-receipt.py:553`), then reports
  "no evidence the port refuses connections after teardown".

The validator's `--selftest` fixture uses different names (`"json"` rows, `"started"`,
`"port_closed"` at `tests/llamacpp-live/check-receipt.py:595`, `:632`, `:668`), so selftest green
does not detect the drift — an instance of `PROTOCOL.md:403` ("Self-test green is
capability, not a measurement"). Consequences for box 2: the receipt's own `checks` array
can still support the execution claim, but a LOG/pointer claim of "receipt validated" is
false until L1 reconciles the names or the owners fix them; do not pre-write validator
exit 0. This is a cross-item defect for `LiveHarness` + `LiveReceiptGate`, not a run
failure. **[INFERENCE from static code; not executed]**

### F2 — High — no lane-side mark may move to `[x]`

`PROTOCOL.md:63-64`: "Every `SHONEN.md` box checked by a reviewer who did not author the
round's changes"; `PROTOCOL.md:64-65`: "a subagent the lane dispatched is still the lane".
The C2 executor, the receipt validator, this seat, and L1's round integration (the lane's
round owner) are all lane-side. Only a fresh lane or the fleet integrator's review may write
`[x] <verifier-id>`; an `[x]` without a named non-author counts as `[~]` (`PROTOCOL.md:63-67`).

### F3 — Medium — development runs are not the measurement

The C2 contract allows the author to run the harness for development but says "such runs are
not measurements" (`.ufo/waves/round-16/build/spec.json:59`). The SHONEN pointer and LOG entry must
cite L1's measurement receipt; if two receipts exist, name the measured one by path and
time. `PROTOCOL.md:374` ("A command offered as evidence is a re-run performed at write
time") bars citing a remembered run.

### F4 — Medium — `loading_observed` is conditional; C1's matrix is not box 2's evidence

The receipt records loading observed/not-observed; the contract makes it "never required"
(`.ufo/waves/round-16/build/spec.json:59`). Even `true` only proves the server emitted the
loading body: the probe runs after `/health` 200 (`tools/kama-llamacpp-live.py:693`,
`:742`), so this receipt never exercises `MODEL_LOADING` live. Do not write "loading
verdict validated live" for either value, and do not use a live 503 to replace the C1
stub-matrix envelope calibration; one live response is corroboration, not the matrix. The
current box-2 pointer does not mention loading, and the replacement should not either
beyond the measured boolean.

### F5 — Medium — scope overreach toward consumer endpoints remains the live risk

The registry rows are still `DEAD` and say so
(`registry/endpoint-consumers.tsv:35-37`, "sampled DEAD in registry/history/latest.tsv";
"runtime readiness must be re-probed"). `PROVINCE.md:24-25`: "Serving runtime is explicitly
unavailable on the concrete surfaces". If the new pointer drops the old `DEAD` caveat
(`SHONEN.md:8`) without saying "registered-consumer reconciliation" is excluded, a reader
can mistake a lane-owned control for endpoint recovery. The proposed text keeps that
exclusion explicitly.

### F6 — Medium — the validator is same-lane tooling, not an independent check

`tests/llamacpp-live/check-receipt.py:352` is being written in this same wave
(`.ufo/waves/round-16/build/spec.json:64`); it is designed to re-derive probe verdict/exit
from stored output, which is a real consistency check, but the current pair does not agree
on the receipt fields (F1a), so its exit 1 on a green run is a contract defect, not a run
failure; `PROTOCOL.md:403` says "Self-test green is capability,
not a measurement". Record its exit 0 only after F1a is reconciled; until then record the
INVALID output and route it. Never present it as the non-author admission of box 2.

### F7 — Low — "non-consumer port" needs the registry sweep, not only the validator

The validator checks only "port not 8080/34113" (`.ufo/waves/round-16/build/spec.json:64`). The C2
harness also refuses "any port number appearing in registry/endpoint-consumers.tsv", but
that is construction, not a receipt check. Today the registry has only 8080/34113
(`registry/endpoint-consumers.tsv:35-37`), so the two are equivalent now; record the
one-line registry grep in the LOG so the claim remains re-derivable if rows are added.

### F8 — Low — the receipt proves identity/readiness surfaces, not a completion

The nine checks cover `/health`, two `/v1/models` identity facts, `/props` alias,
`/metrics`, the two probe runs, and teardown; `/slots` is captured but not checked, and
there is no `POST /v1/chat/completions` or token generation. Wording
should be "loaded and identified", not "served a request". Kama's province is endpoint
identity/health (`SKILL.md:18-19`), so this is sufficient for the task; it is not a model
quality or inference claim.

### F9 — Low — sequence and timestamp hygiene

Write the receipt first, then the LOG entry, then the SHONEN line; commit the receipt and
the citations together (or receipt earlier). `PROTOCOL.md:371-372` makes a future-dated
evidence timestamp a conformance defect; do not edit the receipt's clock fields after the
fact. If the LOG entry is committed separately, the pointer still resolves at closure, but a
same-commit or LOG-first order keeps the mechanical SHONEN check simple.

### F10 — Low — canonical form is one line, and only one line

The replacement must not become a second indented line or an added bullet:
`PROTOCOL.md:446` confines the file to the seed boxes plus one indented evidence line per
box. The existing four lines all carry prose after the arrow (`SHONEN.md:6`, `:8`, `:10`,
`:12`), so the style is consistent; keep all caveats on that single line.

---

## 6. Residual risk and verification gaps

- **Receipt is self-attesting.** The committed bytes plus the lane validator establish
  internal consistency, not that a process actually ran. A non-author could re-run the
  harness, but the pinned binary/model live outside the repo (`~/.local/opt/llama-b11755`,
  `~/.cache/kama-shokunin/models/stories260K.gguf`); identity rests on the receipt's
  sha256 pins and the public b11755 release. This is the normal evidence standard, not
  cryptographic execution proof. **[INFERENCE]**
- **One build, one model, one ephemeral port.** Extrapolation beyond llama.cpp b11755, the
  tiny GGUF, or a default slot configuration is unsupported. The loading envelope and other
  runtime families remain C1/scout territory.
- **Interpretation risk.** A strict reader of "the domain's actual surfaces" may refuse the
  lane-owned control as box-2 evidence; the receipt cannot settle that. If that happens, the
  box stays `[~]` and the honest next step is a live registered endpoint (operator-owned
  restoration) or an explicit reviewer ruling recorded in the round notes.
- **Not measured here.** This seat did not run `kama-llamacpp-live.py`, `kama-probe.sh`,
  `check-receipt.py`, or any gate. `tools/kama-llamacpp-live.py`,
  `tests/llamacpp-live/check-receipt.py` and the probe edits now exist in the working tree,
  but no `kama-llamacpp-live/v1` receipt exists at review time. All receipt-field
  statements cite the C2/C2-validator contract (`.ufo/waves/round-16/build/spec.json:59`,
  `:64`) and the current code, not an observed run.
- **In-flight files.** `tools/kama-llamacpp-live.py` was still being written during this
  review (mtime 10:38 local). Line citations are the working-tree state then; the field
  names in F1a were re-checked at that time. If the owners reconcile them before L1's
  measurement, drop the F1a caveat and run the validator once for the record. **[INFERENCE]**
- **Installs:** none.
