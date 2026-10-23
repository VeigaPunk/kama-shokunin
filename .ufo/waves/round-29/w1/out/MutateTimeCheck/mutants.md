# MutateTimeCheck — round 29 wave 1

## Scope, axes, detector

Axes: timestamp-form recall; detector sensitivity; exact-byte restoration.

Attacked the patched `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py`, now committed at `513eba3ba51a142c9936553e3a85918345eb5c4c`. The patch was first inspected as an uncommitted diff, then captured using the parent's updated comparison `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 35b90184 513eba3b -- tools/prereg-time-check.py`.

The frozen patched SHA-256, denoted **P** below, is:

`ca72edf2a210a763c1d8cbc7a57aa70445a2794c195fc288e82d6dfe7d473dd4`

Eight isolated copies were created under `/fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck/`. Each received one behavior-bearing line mutation. No lane source or sibling source was edited. For every copy, the same two-part detector ran on pristine, mutated, and restored bytes:

```text
/usr/bin/python3 /fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck/<ID>.py --selftest --scratch /fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck/selftests/<ID>/<phase>
/usr/bin/python3 /fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck/<ID>.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --path .ufo/waves/round-28/preregistration.json --rev 75b78bb4900aae1edcdb6b229bb8c572c20fcbce --strict
```

The first must exit 0, print `SELFTEST PASS`, and contain no `[FAIL]`. The second must exit 1 and print the exact A1 finding `FLAG line 41: 2026-10-23 ~08:45Z (later than commit by 404s)` plus `RESULT fail: 1 timestamp(s) later than the committer time`. Exit 1 for that historical check is the expected successful detection, not a baseline failure. A mutant is killed only if pristine passes, mutant breaks at least one expectation, and the restored copy passes again. This detector does not compare all selftest report text byte-for-byte.

Each invocation was wrapped in `/usr/bin/timeout --signal=TERM --kill-after=2s 30s /usr/bin/prlimit --as=536870912 --cpu=25 --nofile=128 -- ...`; at most two detector CLI processes ran concurrently. Git directory/worktree/index variables were unset, global/system Git configuration was disabled, and all selftest-created repositories stayed under the assigned scratch directory. The tool's mandated selftest itself uses `git init`. Every saved file is size-bounded below 1 MiB. `/fast` had 69 GiB available before copying. No tools installed or updated; no server or other model runtime invoked.

## Mutation results

All eight pristine copies and all eight restored copies passed both detector parts: selftest exit 0/`SELFTEST PASS`; historical exit 1/exact 404-second A1 flag. There were **5 killed, 3 survived, 0 inconclusive** mutants.

| Mutant | Single-line defect (original tool line) | Mutated selftest exit | Mutated 75b78bb4 exit | Verdict |
|---|---|---:|---:|---|
| M01 | TIME_RE L42: remove ` ~` alternative, retain `(?:T| )` | 1 | 0 | killed by both |
| M02 | TIME_RE L42: remove plain-space alternative, retain `(?:T| ~)` | 0 | 1 | **survived** |
| M03 | TIME_RE L42: remove `T` alternative, retain `(?: ~| )` | 1 | 1 | killed by selftest |
| M04 | parse_iso regex L73: remove ` ~` alternative, retain `(?:T| )` | 1 | 0 | killed by both |
| M05 | parse_iso regex L73: remove plain-space alternative, retain `(?:T| ~)` | 0 | 1 | **survived** |
| M06 | parse_iso regex L73: remove `T` alternative, retain `(?: ~| )` | 1 | 1 | killed by selftest |
| M07 | parse_iso L78: `datetime(y, mo, d, h, mi, 0, tzinfo=timezone.utc)` (discard seconds) | 0 | 1 | **survived** |
| M08 | parse_iso L78: `datetime(y, mo, d, h, 0, s, tzinfo=timezone.utc)` (discard minutes) | 1 | 0 | killed by both |

Actual failure outputs:

- M01 and M04: `[FAIL] flag: space-tilde approximate time after commit (round-28 A1 form): expect 1, got 0`; historical output says `no ISO-8601 UTC timestamps found` and `RESULT pass: no timestamp later than the committer time`.
- M03 and M06: the minute-precision, seconds-precision, and strict-far-future selftest cases each report `expect 1, got 0`. The historical A1 flag remains intact.
- M08: the minute-precision, seconds-precision, and approximate-time selftest cases each report `expect 1, got 0`. Its historical output is `ok   line 41: 2026-10-23 ~08:45Z (at/before commit)` and `RESULT pass: no timestamp later than the committer time`.
- Every killed mutant ends its selftest with `SELFTEST FAIL`; every survivor ends with `SELFTEST PASS`. All mutated detector stderr streams were empty.

### What survived

**M02/M05: plain-space support can disappear without failing the detector.** The added plain-space fixture is only a *past* time. Under either mutant it prints:

```text
[PASS] clean: space-separated time before commit: expect 0, got 0
          no ISO-8601 UTC timestamps found
        RESULT pass: no timestamp later than the committer time
```

The historical check uses ` ~`, not a plain space, so it also passes. This is a coverage finding, not evidence that the patched implementation currently fails that form. The detector does not require the past fixture to have been recognized. A future plain-space fixture and/or an assertion of the extracted finding would distinguish these defects. Neither was added to the lane.

**M07: seconds can be discarded without failing the detector.** This is observably non-equivalent: the pristine strict-far-future selftest prints `later than commit by 212865s`; the mutant prints `later than commit by 212837s` for the same `2026-10-25T14:27:28Z` token. Both still have the expected exit codes, and the historical minute-only token retains its correct 404-second result. A same-minute, one-second-after-commit case or an exact parsed-time/delta assertion would distinguish it. This is a detector limit; the contract was not changed.

Raw outputs and complete argv/exit/status records are under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/receipts/<ID>/<phase>/` as `selftest.out`, `75b78bb4.out`, their `.err` streams and JSON records. Phases are `pristine`, `mutated`, and `restored`.

## Hashes and restoration evidence

For each specimen the sequence was **P → mutant hash below → P**. The detector itself did not change any specimen: its before/after SHA-256 matches within every phase. Whole-file restoration used the untouched `/fast/scratch/hyaku/kama-r29/w1/MutateTimeCheck/pristine.py` and ran even if the mutation detector failed.

| Mutant | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|
| M01 | `4254fcf2a1163f52aa36a218f37d42eb0b057ce2dbad3ade7408222377cb31fd` | P |
| M02 | `b2861d005367cf342311f67ee774dd39b18548e3dbd548edf809e837cab5b617` | P |
| M03 | `5889d52ee1b42d79493711154a6dd1add285d1fc987f916c916bfa912fa282e7` | P |
| M04 | `07e65d5df25d195f66adbcab3890c1932d6865e51628713027fee25499358250` | P |
| M05 | `f63bfb896e918dfff0198b33d370dcd3dc1c95e73dd39f02db3e17b28cb06127` | P |
| M06 | `7a674278000dff2cbe219d0b8714bd6face47e91aad2665a58b03ed1d086a0dc` | P |
| M07 | `2f1a48dafbb384517094c6bea54a004ece17744fb23f93a6a74b9e53beef5085` | P |
| M08 | `b3e22de1fa2c66a4220917aa8122b8a87773daa04fd0cc619552ffdb94b3bdab` | P |

`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/restoration.json` records all eight copies as `exact: true`, with actual before/after digests and copy exits. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/final-source.json` records the lane tool still at P and the untouched pristine snapshot at P. The three phase aggregate receipts are `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/pristine.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/mutated.json`, and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/restored.json`.

## Every preregistration writing revision

Pinned history at observed HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`. The requested Git log returned 13 writing revisions across rounds 24–29. Ran the pristine patched copy against the changed preregistration path at **each** revision, both with the default 86400-second horizon and with `--strict` (26 invocations). No invocation returned evaluation-error exit 2. Times in the following table are the exact extracted tokens; deltas are printed by the tool.

| Writing revision | Round | Default / strict exit | Default flags | Strict-only flags |
|---|---:|---|---|---|
| `827d136546b8` | 29 | 0 / 0 | none | none |
| `75b78bb4900a` | 28 | 1 / 1 | L41 `2026-10-23 ~08:45Z`, +404s | none |
| `d8bf1804ce52` | 28 | 0 / 0 | none | none |
| `1471f6765991` | 27 | 0 / 0 | none | none |
| `a712902cc945` | 27 | 0 / 0 | none | none |
| `6020243e74a4` | 27 | 0 / 0 | none | none |
| `530eaa998735` | 27 | 0 / 0 | none | none |
| `a23c0e042114` | 26 | 0 / 1 | none | L33 `2026-10-25T14:27:28Z`, +212074s |
| `f071209a0f95` | 26 | 0 / 0 | none | none |
| `a12850c5cbc1` | 26 | 1 / 1 | L6 `2026-10-23T03:45Z`, +1517s; L29 `2026-10-23T03:55Z`, +2117s | none |
| `a4a159c39967` | 26 | 1 / 1 | L6 `2026-10-23T03:45Z`, +1569s | none |
| `efe58e96e6cf` | 25 | 1 / 1 | L5 `2026-10-22T08:31:00Z`, +76s | none |
| `d1b9d956a0be` | 24 | 0 / 0 | none | none |

The strict-only round-26 token is explicitly a provider quota-reset time, not a claimed writing time. The default output labels it `future beyond horizon (+212074s)`; this is the documented horizon, not a regex miss or newly established false statement.

History receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/history.json`. Exact version blobs and mode outputs: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/history/`. Enumeration: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/history-log.out`.

### Remaining unrecognized forms found in those bytes

No further missed, fully dated, unambiguous UTC timestamp was found in this 13-version set after the A1 repair. There are narrower residual *notation/semantic limits*; none is promoted to a proved false statement without its missing interpretation:

1. **Undated approximate correction time.** At `f071209a0f95`, round-26 L29 says `corrected at about 03:21Z`. The actual file committer time is `2026-10-23T00:20:14-03:00` (03:20:14Z). The patched tool reports only the fully dated L6/L29 tokens and exits 0 in both modes. **[INFERENCE]** If the bare clock means 2026-10-23 and is interpreted literally to minute precision, it is 46 seconds after that commit; the date is implicit and `about` has no declared tolerance, so this is a candidate missed false-time form, not an unconditional falsification. The same prose persists at `a23c0e042114`, by whose 03:32:54Z commit it is no longer future.
2. **Wildcard minute.** Round-26 L20 at `a4a159c39967` and `a12850c5cbc1` says the pilot ran `at 03:4xZ`. TIME_RE cannot recognize it; these versions already fail for their fully dated tokens. **[INFERENCE]** On the same-day reading, 03:40–03:49 is later than the respective 03:18:51Z / 03:19:43Z commits, but neither the date nor an exact minute is supplied. This is a further review candidate, not an exact parsed timestamp.
3. **Other undated clocks are not additional false-time findings.** Round-26 `about 03:17Z` / `about 03:19Z` and round-27 L49 `05:25:25Z` are not parsed; on their contextual same-day readings they precede their writing commits. Round-26 L29's quoted `03:55Z` / `03:45Z` are explicitly *earlier wrong clock guesses*, so blindly parsing all bare clocks would also flag quoted historical errors. No broader time grammar was proposed as a contract change.

## Delivery boundary

Executed 48 pristine/mutated/restored detector invocations plus 26 historical-version checks. No C1 counter correction/data rows were written or proposed, no frozen counter was changed, and no integration or shipping judgment is made. The evidence runner is retained at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/probe.py`; the captured patch is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/MutateTimeCheck/source.diff`. This assignment ends with these mutation and history findings.
