# Simp1 — YAGNI review of the round-49 tools (kama, round 49 w1)

**Verdict:** the round-49 code in the three tools is nearly free of dead weight — four
deletions are safe and worth taking (net −8 lines, no behaviour change, both frozen
counters unchanged), and the three candidates the ticket named (two binders, the
`ARCHIVE_MAX_BYTES`/`MEMBER_MAX_COUNT` pair, the v2/v3 docstring history blocks) must be
**kept**: each is load-bearing for the frozen counter contract or for provenance that this
seat's charter forbids deleting. One real doc defect found (a stale `status` definition that
contradicts the code).

Base: lane commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (round-49 build).
All measurements in my own `git clone --shared` at that commit under
`/fast/scratch/hyaku/kama-r49/Simp1/lane`; the diffs are commit-to-commit, so they do not
depend on the shared tree. I issued no write to the shared lane (every lane file I read was
already dirty from other seats — K2Negation, V1Live, X1Selftest — when I first read it; the
git-ignored `tools/__pycache__` there carries several interpreters' entries and is not
attributable to this seat).

## 1. Proposed deletions (safe set) — `proposed-deletions.diff`

| # | file:line (at 74558c71) | deletion | why it is dead weight | evidence |
|---|---|---|---|---|
| D1 | `tools/append-only-audit.py:24,58` | the two wrappers `v3 (round 48) text, kept:` / `v2 (round 47) text, kept:` + their blank lines (4 lines) | each wrapper duplicates the dated heading *immediately below it* (`:26` "v3 (round 48) grades…", `:60` "v2 (round 47) replaces…"); the history blocks themselves stay | docstring only; `--help` uses `__doc__.split("\n")[0]` (`:958`), byte-identical before/after |
| D2 | `tools/append-only-audit.py:91` | `  status       restored (max == \|D\|), …` | **defect**: this is a second `status` definition (the operative one is `:51`, over `\|G\|`), and it contradicts the code — `:488-490` derives status from `ng = |G|` and emits `ungraded` when `\|G\| == 0`, a state `:91` cannot express | deleting it leaves `:51` as the single definition; selftest 30/30 unchanged |
| D3 | `tools/kama-llamacpp-live.py:287-288` | `'written_utc': _utc_now()` in `ready.json` | no reader anywhere: the counter reads only `pid`/`port` (`tools/round49-replay-witness-audit.py:306-307`), the build spec names `{schema, port, pid}`, and `grep -rn written_utc tools/*.py` finds only this producer plus an unrelated fixture literal in `tools/prereg-time-check.py:198` | live run before/after: `ready.json` key delta = `['written_utc']` and nothing else (`evidence/witness-compare.txt`) |
| D4 | `tools/kama-llamacpp-live.py:240-243, 264-267, 302-306` | three copies of the chunked-sha256 idiom → one `sha256_stream(fh)`, `sha256_file()` delegating to it | the round-49 change had to hash a descriptor and a member without re-opening, so it inlined the loop twice next to the pre-existing copy in `sha256_file`; the idiom (1 MiB chunks, `hashlib.sha256`, `iter(lambda…, b'')`) is now stated once | identical digests: selftest 30/30 + C1's three witnessed replays and its archive cap leg all pass after the change |

Net: `tools/append-only-audit.py` −5, `tools/kama-llamacpp-live.py` +13/−21 → **net −8 lines**
(`git diff --stat 74558c71 98b10934`). `append-only-audit.py`'s docstring 120 → 115 lines
(`ast.get_docstring`).

## 2. Optional tightening — `optional-server-size-required.diff` (take or drop)

`verify_archive_member(..., server_size=None)` (`tools/kama-llamacpp-live.py:212`) makes the
round-49 size bound skippable: the guard is `if server_size is not None and found.size !=
server_size` (`:262`), and six selftest cases already call it without a size. Every
production call passes it (`:1666`). Making the parameter required deletes the default and
the `is not None` branch, so a future caller cannot silently lose the bound. Cost: the
seven selftest tuples carry `size` explicitly (eight on the integration tree, which adds
X1Selftest's member-count case). Independent of §1; both were measured together and
separately.

## 3. Candidates named by the ticket that I deliberately KEPT

1. **Two binders** (`tools/append-only-audit.py:202-234` `row_token`/`NEG_WINDOW`/`binds`
   vs `tools/round49-append-audit-v4-check.py:107-131` `token`/`says`/`binds`). Not
   deletable: the frozen counter's own docstring freezes the design — "recomputes them on
   its own code path" — and the tool is the older authority. Deleting either copy (e.g. by
   importing the counter from the tool) would make the measuring instrument a library of the
   measured tool and void the independence claim, for 25 duplicated lines. What *is* worth
   keeping an eye on is agreement: the two bodies are line-for-line equivalent today; the
   integration edit now in the shared tree (K2Negation F1) widens only the tool's
   `NEG_WINDOW`, so the two no longer agree on `cannot`/`can't`/curly apostrophes/en-dashes.
   That is a calibration asymmetry for L1 to record, not something this seat may touch.
2. **`NEGATIONS` vs `NEG_WINDOW` overlap** (`tools/append-only-audit.py:141` vs `:212`). I
   measured the redundancy instead of asserting it: over **4,191,050 lines in 24,597 files**
   at the tip, the four fixed strings fire on **0** lines the regex does not already catch
   (regex-only: 237 lines, e.g. "does not prove append-only"; both: 147)
   (`evidence/negation-differential.txt`). So the tuple is unreachable on the lane's own
   text — but the frozen counter's definition says "v3's four fixed strings still apply"
   and its binder keeps them (`round49-append-audit-v4-check.py:90,115-117`). Deleting them
   would bind, in the tool, lines the counter unbinds, for a saving of one line. Keep.
3. **`ARCHIVE_MAX_BYTES` / `MEMBER_MAX_COUNT`** (`tools/kama-llamacpp-live.py:208-209`).
   These bound two different unbounded axes — bytes on disk before hashing (`:233`) and
   index entries after decompression (`:252`); neither implies the other (a 1 GiB gz can
   hold millions of empty headers). Not YAGNI: they are the round-49 answer to the class the
   counter asks about. Coverage note for a later round (not a deletion): `provenance-archive-too-large`
   is the one round-49 token no selftest exercises; `-too-many-members` now gets a case in
   the integration tree (seat X1Selftest).
4. **The v3/v2 history blocks** (`tools/append-only-audit.py:26-91`, 45 lines). They are
   explicitly marked historical and still define what v4 only amends (`region`, `section`,
   `count`, `eligible`, `graded`, `ungraded`); deleting them would remove the definition of
   the current carve-out and the provenance of rounds 46-48. I removed only their duplicate
   labels (D1) and the one statement v3 superseded (D2).
5. **`res["witness_dir"]`** (`tools/kama-live-replay.py:279`) and the receipt's
   `witness.{schema,dir,port,pid}` (`tools/kama-llamacpp-live.py:298-300`): unread by code,
   but they are the durable record (the counter reads `released` only,
   `round49-replay-witness-audit.py:325`; the wave's X1Timeout seat is specified to read
   `released`/`waited_ms`). Removing them would leave the receipt unable to say which pid it
   held once the witness dir is gone. Keep.

## 4. Behaviour-preservation evidence (all commands run in my scratch)

* Selftests, landed vs proposed (`evidence/selftest-*.txt`):
  * `python3 tools/append-only-audit.py --selftest --scratch $S/st-aoa` →
    `AOA_SELFTEST pass=30 fail=0`, exit 0; byte-identical output before/after
    (`diff base-aoa.txt after-aoa.txt` empty).
  * `python3 tools/kama-llamacpp-live.py --selftest` → `selftest: ok`, exit 0; identical
    apart from the ephemeral tcp6 ports it prints each run (both sides print the same shape).
  * `python3 tools/kama-live-replay.py --selftest --scratch $S/st-rep` →
    `KLR_SELFTEST pass=22 fail=0`, exit 0; byte-identical before/after.
  * `append-only-audit.py --help` byte-identical (same sha256 prefix `5f4eaed5465c511e`).
  * `pyflakes` clean on both modified files; `vulture --min-confidence 60` finds nothing new
    in the round-49 code (only pre-existing `health_res`, `redirect_request`).
* Frozen counters, landed `74558c71` vs proposed `c9ac0612` (= landed + §1 + §2), same
  clone, full lane history:
  * C1 `python3 tools/round49-replay-witness-audit.py --repo $S/lane --tip <c> --scratch $S/c1*`
    → both `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, exit 0; three witnessed
    replays each (`evidence/c1-base-74558c71.txt`, `evidence/c1-after-c9ac0612.txt`).
  * C2 `python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip <c> --scratch $S/c2*`
    → both `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0; the lane detail is identical
    line for line: `events 5 bad_declarations 0 regressed 0 ungraded_lines 82`, events
    `dd9f5dc6c0e6` 17/23 and `0718b6abbda6` 65/65 (`evidence/c2-*.txt`).
* Witness path end to end, real b11909 server on loopback + the frozen 1.1 MB model, an
  observer that reads `ready.json`, `/proc/<pid>/exe`, `ss -ltnp`, POSTs `/tokenize`, then
  writes `release` (`evidence/witness-compare.txt`, `evidence/witness-live-*.json`):
  landed and modified runs both exit 0 with `witness.released true`, `waited_ms 300`,
  `port_listener_ownership child`, no failed check, `teardown.port_refuses true`; the only
  observable difference is the deleted `written_utc`. A third run saw
  `LISTEN … 127.0.0.1:35925 … ("llama-server",pid=1559046,fd=3)` and 7 tokenizer tokens.
* Diff portability: §1 applies to the **current integration working tree** (which already
  carries V1Live's fd/`O_NONBLOCK` rework and X1Selftest's member-count case) with offset —
  `deletions-on-integration-snapshot.diff`; on that snapshot the aoa selftest is 30/30, the
  live selftest `ok`, pyflakes clean, and C1 still `witness=1 cap=1 newrow=1 witnessed=3/3
  met=True` (`evidence/c1-integration-snapshot+deletions.txt`). C2's **fixture** leg is
  8/8 there; its **lane** leg cannot be evaluated on that snapshot (a fresh 2-commit repo has
  no history, so `events 0`) — the lane leg was measured on the real history above.

## 5. Tradeoffs / notes for L1

* D2 is a documentation deletion that also removes a false statement; if L1 prefers to keep
  a status line in the v2 definitions block, it must be reworded to |G| and to include
  `ungraded`, not left as is.
* D3 changes an artifact field, not just prose: `ready.json` loses `written_utc`. Nothing
  reads it and the receipt keeps `started_utc`/`ended_utc`/`waited_ms`, so the timestamps
  remain reconstructible from the receipt.
* The optional §2 changes a signature; if not taken, the `server_size=None` default remains
  a way to skip the round-49 size bound — worth at most a comment if dropped.
* Only deletions and one tightened signature are proposed. No counter, preregistration or
  control file was touched; nothing was written to the lane, the fleet repo or the lane's
  index/jj state. No tools were installed or upgraded for this seat.
* Applying: `proposed-deletions.diff` applies cleanly to `74558c71`; the optional diff
  stacks on it (`git apply proposed-deletions.diff && git apply
  optional-server-size-required.diff`), or use `proposed-deletions-all.diff` in one shot.
  Both were verified on a fresh `git archive 74558c71` tree with the selftests above
  (`evidence/apply-check.txt`). For the current integration tree use
  `deletions-on-integration-snapshot.diff` (safe set only).

## 6. Paths written

* `.ufo/waves/round-49/w1/out/Simp1.md` (this report)
* `.ufo/waves/round-49/w1/out/Simp1/proposed-deletions.diff` (safe set, against `74558c71`)
* `.ufo/waves/round-49/w1/out/Simp1/optional-server-size-required.diff`
* `.ufo/waves/round-49/w1/out/Simp1/proposed-deletions-all.diff` (both, against `74558c71`)
* `.ufo/waves/round-49/w1/out/Simp1/deletions-on-integration-snapshot.diff` (safe set,
  rebased onto the current integration working tree)
* `.ufo/waves/round-49/w1/out/Simp1/evidence/` (selftests before/after, `--help`, C1/C2
  receipts at base and after and on the integration snapshot, witness receipts and
  comparison, negation differential, apply checks)
