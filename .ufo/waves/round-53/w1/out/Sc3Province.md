# Sc3Province — PROVINCE check, round 53

**Verdict: yes — round 53's new surface sits inside `PROVINCE.md` as written; no boundary, refusal or write-boundary change is needed. One append-only record is proposed (exact text below and in `out/Sc3Province/`) solely to keep the file self-describing per its own instrument-landing convention, which rounds 46–48 followed with in-place cell edits.**

Seat item: does round 53's new surface — (A) verifying the code a local model server
executes against its release archive through process memory, and (B) resolving the
lane's own evidence pointers — sit inside `PROVINCE.md` as written? Base
`4229ea1b9a789148dded1f159c20967d9a01373f`, freeze `d01b2b6d48a54ffe0e475000737d3e302c62e28e`,
build `c22602bd8d83ab26349d1087e916ca537ee4f9d1`.

## Evidence

1. `PROVINCE.md` is unchanged by the round-53 build:
   `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 4229ea1b c22602bd -- PROVINCE.md`
   → empty, exit 0. The build touched only
   `tools/{kama-llamacpp-live,kama-live-replay,round53-replay-code-audit,round53-cited-path-check}.py`,
   `registry/cited-path-corrections.tsv`, `SKILL.md` (2 lines), `SCORECARD.md` (+4),
   `corpus/SOURCES.md` (+4), `corpus/lessons/round-53.md`, `.ufo/waves/round-53/*`
   (`git diff --stat` base→build, 18 files, 4515 insertions).
2. Domain as written (`PROVINCE.md:1-3`): "local model serving & endpoint health —
   local LLM endpoints, baseURL drift, served-model reconciliation, probe conventions."
3. Owns table already holds (`PROVINCE.md:12`) "served-model-id reconciliation
   (`GET /v1/models` vs `--alias` vs the configured model id)" and (`PROVINCE.md:17`)
   the lane-instruments row naming `tools/kama-live-replay.py` "(re-acquire a live
   receipt's server archive and model from the URLs its provenance records, verify
   both sha256 values, re-run the lifecycle and compare every check; round 47)".
4. Boundary rule as written (`PROVINCE.md:45-46`): kama answers *"is the thing at
   this baseURL the model this config believes it is, right now"*.
5. Refuses as written (`PROVINCE.md:42-44`): model quality/eval (kengaku), credentials
   (kagi), dispatch (kumitate), remote web surfaces (kake). Write boundary
   (`PROVINCE.md:47-51`): never writes `~/.config`, `~/.omp`, systemd. Out-of-province
   rule (`PROVINCE.md:53`): report, never absorb.
6. Fixture governance as written (`PROVINCE.md:57-86`, round-16/17/18 notes): the
   lane-owned llama-server child on an unregistered loopback port, torn down in the
   same run, **pending L0 ratification** — the same fixture both round-53 tools use.
7. Round-52 routed lineage: `corpus/lessons/round-52-verifier-spotcheck.md:135-139`
   (R2 carried item "libraries and model load by path (K2Design)" — round-53 C1's
   target); `corpus/lessons/round-52.md:58` (Mistakes #4 — seat W3Mistakes'
   `cited-path-exists.py`, round-53 C2's routed origin).
8. Counter docstrings (the contract) describe lane-internal methods only:
   `tools/round53-replay-code-audit.py:1-64` — reads each executable range of the
   replay's own server from `/proc/<pid>/mem` (Yama ptrace_scope 0/1, the counter is
   the server's ancestor) and compares with its own archive download; classifies all
   other mappings as root-owned/not-writable host files; scratch-only, read-only on
   `--repo`. `tools/round53-cited-path-check.py:1-83` — parses backtick citations in
   `SCORECARD.md`/`SHONEN.md`/`SKILL.md` outside fences, resolves against the lane
   tree then the fleet tree (`scripts/`, `templates/`), re-derives ledger classes
   from git history; read-only on `--repo` and `--fleet`; the `upstream` class fetches
   pinned raw.githubusercontent.com URLs.
9. Measured receipts at the build (copied to `out/Sc3Province/c1-build.out`,
   `c2-build.out`): C1 `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3
   sealedruns=3/3 coderuns=3/3 met=True` exit 0 — 8 archive libraries byte-equal in
   `/proc/<pid>/mem`, 13 root-owned host files; C2 `fixture=1 lane=1 scenarios=8/8
   cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0
   met=True` exit 0.
10. Convention check: rounds 46, 47, 48 each updated only the lane-instruments cell of
    the Owns table in place (`git show 4340cf2f/383f1fc7/c4b2175d -- PROVINCE.md` —
    single-line cell edits, no appended notes); notes were appended in rounds 16-43.
    `PROVINCE.md` is not in the append-only contract (`grep PROVINCE
    registry/append-only-contract.tsv` → no rows), so neither form is contract-graded;
    the cell edit is the file's own instrument-landing practice.

## Analysis

**Surface A (C1, executing-code identity) — inside.** It answers the province's own
boundary question one layer deeper than the owned row at `PROVINCE.md:12`: not "which
model id does the endpoint serve" but "is the code the lane-owned server executes the
release archive's own bytes, right now" — the direct continuation of the round-47
instrument already named in the Owns cell (`PROVINCE.md:17`), attacking the round-52
routed closure R2. The fixture, its unregistered-loopback port and same-run teardown
are the round-16 discipline verbatim; reading `/proc/<pid>/mem` of its own child is a
read-only inspection of a process the lane started (precedent: procfs listener
ownership, round-18 note), crossing no write boundary and sampling no registered
consumer or other endpoint. Downloads are the same archive/model URLs the round-47
instrument already re-acquires. No refused surface is touched: this is code identity,
not model quality, credentials, dispatch, or a remote web surface.

**Surface B (C2, evidence-pointer resolution) — inside, squarely.** The lane-instruments
row is defined as "the capability repertoire, `SCORECARD.md` canonical list"; C2 is the
same class as the already-named meaning-graded registry checker (round 32), the
digest/hexrun ledgers (rounds 42-43) and the append-only audit (rounds 46-48): a
lane-internal calibration instrument that reads the lane's own committed documents and
git history and discloses its own citation misses. Fleet-tree resolution is read-only
("report, never absorb" honored — it claims no fleet surface); the five upstream raw
URL fetches read pinned source URLs the lane already cites as evidence rows, sampling
no endpoint.

**No boundary change is needed.** The domain sentence, the boundary rule, the refuses
and the write boundary all already cover both surfaces as written; nothing in round 53
expands the province, contracts it, or touches a refused lane.

**Documentation gap (the sentence that is proposed).** Per the file's own convention,
each landed instrument is named in the lane-instruments cell (rounds 42, 43, 46, 47,
48). Round 53 landed two instruments — `tools/round53-replay-code-audit.py` and
`tools/round53-cited-path-check.py` — and extended two owned tools with new receipt
fields (`code_mappings`, `own_code`), but `PROVINCE.md` was not updated, and the
round-53 integration item list does not name it. This is a self-description gap, not a
scope breach. Exact append-only-form text is below and in `out/Sc3Province/`.

## Proposed sentence (append-only form)

Cell addition to the lane-instruments row (`PROVINCE.md:17`), consistent with the
rounds 46-48 in-place cell edits (full unified diff, context verified byte-equal
against `PROVINCE.md:17` — `cmp` in this seat's run):

> `tools/round53-replay-code-audit.py` with `tools/kama-llamacpp-live.py` `code_mappings` and `tools/kama-live-replay.py` `own_code` (every executable mapping of the running lane-owned server read from /proc/<pid>/mem and verified byte-equal against the counter's own download of the release archive, other mappings classed as root-owned host files; round 53), `tools/round53-cited-path-check.py` with `registry/cited-path-corrections.tsv` (every lane-root or fleet scripts/templates path cited outside fences in SCORECARD.md, SHONEN.md and SKILL.md resolves in the lane or fleet tree, or its miss is disclosed with a class git history re-derives; round 53)

Optional appended record note (the fuller form, in the style of the round-16..43
notes; full text in `out/Sc3Province/province-round-53-note.txt`):

> **Round-53 note — executing-code identity and evidence-pointer resolution (2026-10-27).** `tools/round53-replay-code-audit.py` (with `tools/kama-llamacpp-live.py` `code_mappings` and `tools/kama-live-replay.py` `own_code`) verifies that every executable mapping of the lane-owned fixture's server — read from `/proc/<pid>/mem`, compared with the counter's own download of the release archive — is either an archive member (the server implementation, ggml, ggml-base and a ggml CPU backend among them) or a root-owned host library, closing the round-52 routed closure R2 ("libraries and model load by path"); and `tools/round53-cited-path-check.py` with `registry/cited-path-corrections.tsv` resolves every lane-root or fleet `scripts/`/`templates/` path the self-assessment cites outside fences in `SCORECARD.md`, `SHONEN.md` and `SKILL.md`, disclosing each miss with a class git history re-derives (round-52 lesson Mistakes #4, seat W3Mistakes' prototype). Both are lane-internal methods on the round-16 fixture and the lane's own documents: no registered consumer or other endpoint is sampled, the fixture's unregistered-loopback and same-run teardown discipline is unchanged, and nothing is written under `~/.config`, `~/.omp` or systemd. Refused surfaces untouched: this is code and citation identity — not model quality, not credentials, not dispatch, not a remote web surface. Frontier unchanged: other engines and builds, K05, `/v1/completions`.

## Notes

- `pgrep -af llama-server` at seat end shows only seat K2Design's fixture processes in
  K2Design's scratch; this seat started no server and ran no counter (its question is
  the province text; the L1's committed measured receipts are the claim evidence and
  are copied unmodified into `out/Sc3Province/`).
- No tools were installed or upgraded this seat.

## Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province/c1-build.out` (copy of L1 receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province/c2-build.out` (copy of L1 receipt)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province/province-cell-round-53.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province/province-round-53-note.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/Sc3Province/province-round-53-proposal-README.txt`
