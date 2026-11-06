# CR02ClaimC2 — attack on C2 (router error signatures, kama round 89)

## Scope

Attacked the C2 claim only: `tools/round89-signature-rows.py` binding 8 SKILL.md rows under
`## Router error signatures (llama.cpp router mode)` to `.ufo/waves/round-89/measured/router-signatures.jsonl`
at M2=`21b9e36d6192e0a691550b32e0e6c38412227f4c`, witness F=`4eb75c62…`, base=`56174a1f…`.
Five probes: (a) independent receipt recapture, (b) counter at M2/base/HEAD, (c) a 20-case forgery
battery on scratch fixture repos, (d) every Trigger/Action cell against S583 (`server-models.cpp`,
`server-http.cpp`) and against live lane-owned b12177 children, (e) whether the rows are decision rows.
No frozen predicate was altered. Lane read-only; fixtures and receipts are in my out dir.

## Commands and outputs

1. `python3 tools/round89-router-signatures.py --out <out>/sig-recapture.jsonl --work <scratch>`
   → `ROUTER_SIGNATURES calls=9 build='version: 0.9.0-dev (build 12177, commit 6c01da627)'`, **exit 0**.
   Independent JSON diff vs the committed receipt: 9/9 keys equal, **0 diffs** on (endpoint, http,
   error.message); every `body` is **byte-identical**. Receipt is reproducible on this host.
2. `python3 tools/round89-signature-rows.py --repo . --rev 21b9e36d…` →
   `SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0`, **exit 0**. At base `56174a1f…` →
   `rows=0 bound=0 unbound=0 duplicates=0`, **exit 1**. At HEAD `c8db858…` → same 8/8/0/0, **exit 0**
   (SKILL.md and the receipt are unchanged M2..HEAD).
3. Counter bytes at F, C1-M, M2 and the worktree are all sha256
   `30f3af7fb9778024748df46b975da16ab9be654ba0bafc8476e04be134d7f935` — K1 clear.
4. Forgery battery, 20 fixtures (`git init` in `mktemp -d`, toplevel asserted, counter run at `HEAD`):
   caught (exit 1): fabricated message, wrong code, source text instead of wire text, wrong
   `server_sha256`, missing receipt, duplicate row, row outside the section, substring prefix,
   case change, pipe-in-cell, absent receipt path. **Not caught (exit 0): T10/T19, T12, T13, T14, T18, T20.**
5. Live children (lane-owned ports, `start_new_session`, killed by process group):
   `badhdr` completion → 500 `model name=badhdr failed to load`; entry then
   `value=unloaded, failed=true, exit_code=1`; probe at M on that entry → `MODEL_UNLOADED router-unloaded-failed`.
   Probe on unknown id → `MODEL_MISMATCH served-id-mismatch`. Probe on no-autoload unloaded → `MODEL_UNLOADED router-unloaded`.
   Any unknown route → identical 404 `{"message":"File Not Found","type":"not_found_error","code":404}`.
   Single-model server without a `model` field (and even with a wrong one) → 200.

## Findings

**F1 DEFECT — row 2's Probe-verdict/Action cell is wrong for the state it names.**
`SKILL.md:1820` says `MODEL_UNLOADED` / `router-model-missing` or `router-model-invalid`; *"afterwards
the entry is `unloaded` + `failed: true`"*. Those two halves are mutually exclusive. `kama-probe.sh:702`
skips the file-state branch when `failed=1` and `:708`/`:722` then emit `router-unloaded-failed`. Live:
`SIGNATURE_ROW`-independent probe run returned `MODEL_UNLOADED router-unloaded-failed` for the exact
post-failure entry. `router-unloaded-failed` appears **nowhere** in SKILL.md, the knowledge doc or the
lesson (`grep` empty), so an operator reading the row is told to expect a reason the probe will not
print. The verdict (`MODEL_UNLOADED`) is still right, so C1's oracle and the C2 counter are unaffected.
Evidence: `out/action-cells.out` (D2), `out/source-check.txt`, `kama-probe.sh:702,708,722`.

**F2 DEFECT — the `<id>` token binds a message that was never on the wire.**
The substitution is `message.replace("<id>", L.request.model)`, and the `missing-model-field` receipt
line has **no** `request.model`, so `<id>`→`""`. A single-row fixture with message
`model name is missing from the request<id>` binds, **exit 0** (`out/forgery-confirmations.out` T19).
The same holds for any receipt line with an empty/missing `request`. No committed row exploits this, so
the C2 predicate still measures 8/8 — but the counter's intent ("`<id>` is the requested model") is not
enforced, and a future row can append `<id>` to bind.

**F3 DEFECT — 4 of the 6 columns are unverified; a deliberately false Trigger still binds.**
The counter reads only endpoint, HTTP and message. Fixture T18 — correct message, trigger *"the server
binary is missing"*, action *"ignore it"* — binds, **exit 0**. This is the structural reason F1 exists:
the claim's binding cannot detect a wrong Trigger or Action, so "8/8 bound" is a statement about one
column, not about the rows' usefulness.

**F4 NOTE — duplicate detection is string-exact and bypassable.**
`model name=<id> failed to load` and `model name=badhdr failed to load` both bind to the same receipt
line with `duplicates=0`, **exit 0** (T12). Under the frozen definition (exact tuple) this is not a
violation; it does let two restatements of one signature pass as two rows.

**F5 NOTE — provenance is a writable string, not a capture.**
Answering (c) honestly: a hand-written receipt **is not distinguishable**. T13 (one line, `server_sha256`
= the pin, message never captured) binds, **exit 0**; T14 (correct sha, `build` = "totally-not-b12177")
also binds — `build` is never checked; T20 (a crafted `my.jsonl` inside the fixture repo) binds. The one
real defence is F5's converse: I *re-ran* the capture and got byte-identical answers, so the committed
receipt is genuine on this host. The counter alone cannot tell a genuine receipt from a forged one.

**F6 NOTE — the cells the task flagged as suspect are correct.**
- Row 7 (404 `File Not Found`): `server-http.cpp:200-213` rewrites **every** 404 body to that string, so
  the SKILL explanation is right, and the Action ("same body as an unknown route") is verified live —
  `/models/loadx`, `/models/unloadx` and `/totally-not-a-route` all return the identical body.
- Rows 1/3/4/5/6/8 map 1:1 onto `server-models.cpp:1962, 1956, 1951, 2273, 2269, 2125`; row 4's
  parenthetical ("a single-model server accepts it") is true (200 with no `model` field, and with a
  bogus one). Row 2's `400`-not-`404` unload note matches `:2269` `ERROR_TYPE_INVALID_REQUEST`.

**F7 NOTE — depth (e).** Genuine but partial. Rows 1–3 are decision rows that name the probe verdict the
operator must emit; rows 5–8 are correct operator actions; the 404 trap is real value. Against that: the
actionable half is unbound (F3), one Action is factually wrong (F1), and the reason vocabulary is
missing `router-unloaded-failed` — the one string a post-failure operator actually sees (F1). So C2 is
more than bookkeeping, but the "8/8 bound" number overstates what was checked.

## Deliverables

`out/CR02ClaimC2/`: `sig-recapture.jsonl`, `forgery-battery.out`, `forgery-adversarial.out`,
`forgery-confirmations.out`, `action-cells.out`, `single-model.out`, `source-check.txt`.
Scratch `/fast/scratch/hyaku/kama-r89/CR02ClaimC2` removed. No tool installs were needed.

VERDICT: holds — C2's frozen predicate reproduces exactly (8/8/0/0, exit 0 at M2; 0/0/0/0 exit 1 at base; counter sha unchanged F→worktree) and the receipt recaptured byte-identically, but only 3 of 6 columns are actually bound: row 2's Action cell names the wrong reason (`router-unloaded-failed` is undocumented) and the `<id>` token plus string-exact duplicate check are real but unexploited gaps.
