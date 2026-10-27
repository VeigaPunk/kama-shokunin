# round-4 re-census — source-root derivation already correct; endpoints dead

2026-10-14. Steered round 4. Advisory inventories:
`../.ufo/waves/shokunin12h-20261014-p1-repair/members/Kama*.md`.

## Verdict lines (measured)

- `bash tools/kama-probe.sh consumers` → exit 0; `$UFO_SRC` rows resolve
  `file_match=yes` against `~/Projects/ufo-fsd-alpha` (HEAD `964f443e`).
- `bash tools/kama-probe.sh check` → **exit 2** (`DEAD` / connection-refused) —
  the correct identity verdict while nothing serves; not a probe defect.
- `bash tools/kama-probe.sh listeners` → exit 0 (`FOREIGN_SERVICE` on a
  non-model port, classified, not a fault).
- `bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0`.

## No repair warranted

`tools/kama-probe.sh` already implements the authorized order — explicit
`--ufo-src` (bad override dies at parse) → `$UFO_SRC` (dir-only) → first
existing of `~/Projects/ufo-fsd-alpha` then `~/Projects/origin-work/ufo-fsd-alpha`
→ fail-closed. Re-repairing it would be churn.

## Named debt

Dead positive controls (`ufo-fsd-thetick`, `ufo-fsd-local-helper`): correct pin,
dead endpoint. `qwen-coder.service` gone; `34113` and `8080` refuse. Unblock:
operator restores a serving unit. Province contraction remains an L0 decision.

Stale live prose recorded, not rewritten: `SKILL.md` still teaches a live
11-row `MODEL_OK` world; `PROVINCE.md:10-11` owns deleted host pins;
`endpoint-identity.md` line citations drifted (`:481-487` is the match path).

## Independent audit erratum (appended 2026-10-14)

Independent audit: gates re-ran green/expected (consumers 0, check 2 DEAD, listeners 0, snapshot pass=24 fail=0, `bash -n` clean). Identity/pathspec/record confirmed. Dead-path sweep found **46 unique lines** still reading as current locations (`SKILL.md:222` janitor-path checklist greps, `consumer-registry.md:111-119` lowercase `~/projects/shokunin/...`, `listener-census.md:122` + `round-1.md:69` origin-work as live) — named debt, owner kama, unblock: rewrite those lines to the capital-P path or mark them historical. Also corrected in this round: `endpoint-identity.md` cited `tools/kama-probe.sh:481-487` for `schema-unrecognized`; the real site is `:516`.

### Audit detail (appended 2026-10-14)

Historical-marking audit: describe-don't-pin holds for missing-file content hashes
(no md5/sha256 of a missing file is asserted as current identity) and FAILS for
unmarked current claims. Still present tense: `lessons/round-1-citations.md:78`
calls the round-2 probe hash current (`SCORECARD.md:10` pins the later digest);
`SCORECARD.md:12` says `SKILL.md` is 323 lines / 11 error signatures where `wc -l`
is 329 and `:152-163` holds 12; `SKILL.md:33-54,:66-67,:90,:114,:161,:186-188,
:196-198,:203,:213,:222-223,:264-265,:326` still carry pid 1299, `MODEL_OK` on
34113, Jitsi on 8080, the 11-row tally and the `20260929` snapshot as the final
baseline (`curl` to 34113/8080 exits 7; `qwen-coder.service` not-found,
`MainPID=0`; tracked baseline is `20261014T124232Z`); `SKILL.md:120,:317` place
`m_flash` at line 24 (a comment) where the key is `config.yml:433`;
`SKILL.md:93,:101` cite `consumer-registry.md:54-55`/`:49` for rows that live
elsewhere; `endpoint-identity.md:5,:9,:13,:21,:97,:122,:127` and
`snapshot-history.md:15,:21,:36,:53` still point at the wrong probe/census lines
(the `:516` fix covered only one site); `consumer-registry.md:101` locates the omp
default at line 1544771 where the string is at newline-line 1149391;
`drift-timeline.md:24` still calls `opencode.json:158` current though the file is
5 lines. Owner kama; unblock: mark those lines historical and repoint the probe
citations. Dead positive controls remain operator debt.

### Counter-vs-log audit (appended 2026-10-15)

`CVL-DRIVER-AGREE`: `.ufo/state/kama.round` = `1`, the watchdog log's only kama
launch and last wrap are both `round=1`, and `.ufo/reports/round-1/kama.md` titles
itself round 1 — `STATE_COUNTER_LOG_MISMATCH` does not fire. **Record gap (named,
pre-existing):** reports exist for rounds 2 and 4 and `LOG.md` carries headings for
rounds 2, 3 and 4, but **round 3 has no report file** (`CVL-LANELOG-REPORT-GAP`).
That is an absent file, not an unhealthy lane. Unblock: file a round-3 report or
record the omission as debt in the round-4 record.

## Corrections — round 10 (2026-10-19)

*[correction 2026-10-19 (round 10, A44): `SCORECARD.md:10` at line 42 is stale (nl -ba SCORECARD.md | sed -n '10p;19p' => line 10 is current-authority text, while the later probe digest/evidence is at line 19); current anchor: `SCORECARD.md:19`]*

*[correction 2026-10-19 (round 10, A45): `SCORECARD.md:12` at line 43 is stale (wc -l SKILL.md; nl -ba SCORECARD.md | sed -n '12p;21p'; nl -ba SKILL.md | sed -n '167,182p' => SCORECARD 12 is a round-gap note, the current error-signature table is at SKILL 167-182 with 12 entries, and SKILL has 343 lines); its companion `SKILL.md:152-163` now contains the request-time example, not the error-signature table; current anchor: `SKILL.md:167-182`]*

*[correction 2026-10-19 (round 10, A46): `SKILL.md:33-54` at line 44 is stale (nl -ba SKILL.md | sed -n '33,54p;56,61p' => lines 33-54 now give the 2026-10-15 DEAD sample, and the September worked example is explicitly dated at 56-61); the accompanying `:66-67,:90,:114,:161,:186-188` references no longer support the former present-tense claim; current anchor: `SKILL.md:33-54,56-61`]*

*[correction 2026-10-19 (round 10, A47): `:196-198` at line 45 is stale (nl -ba SKILL.md | sed -n '194,213p;220,231p;262,267p;324,330p' => the checklist now reports the three-row DEAD sample, distinguishes dated September examples, and directs readers not to pin old pid/port state); the remaining `:203,:213,:222-223,:264-265,:326` anchors no longer carry the former 11-row current-state claim; current anchor: `SKILL.md:196-213,220-231,262-267,324-330`]*

*[correction 2026-10-19 (round 10, A48): `SKILL.md:120,:317` at line 48 is stale (nl -ba SKILL.md | sed -n '120p;317p'; nl -ba corpus/knowledge/alias-endpoint-normalization.md | sed -n '11p' => those skill lines no longer locate m_flash; the current alias table records its row at 11); the companion `config.yml:433` reference is an external config pointer not re-read under the host-content restriction; current anchor: `corpus/knowledge/alias-endpoint-normalization.md:11`]*

*[correction 2026-10-19 (round 10, A49): `SKILL.md:93,:101` at line 50 is stale (nl -ba SKILL.md | sed -n '93p;101p'; nl -ba corpus/knowledge/consumer-registry.md | sed -n '49p;54,55p;89,107p' => the old skill locations no longer cite those consumer rows, and registry lines 49/54-55 describe remotes/removed checkout rather than the current inventory); the current consumer table is at `SKILL.md:94-103` and `consumer-registry.md:89-107`; current anchor: `SKILL.md:94-103; corpus/knowledge/consumer-registry.md:89-107`]*

## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `47f3aedd6fa3` (round-4: audit corrections — lane-root-resolvable pointers; kotoba index row + tracked_files pin refresh; kama line ref; kasegi census regeneration):

`````text
`.ufo/waves/shokunin12h-20261014-p1-repair/members/Kama*.md`.
`````
