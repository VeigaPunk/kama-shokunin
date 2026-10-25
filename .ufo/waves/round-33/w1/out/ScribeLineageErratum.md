# ScribeLineageErratum — round-33 wave-1 scribe report

Seat: `ScribeLineageErratum` (scribe, leaf; no subagents). Lane: `kama-shokunin`,
read at HEAD `7c35289da5f4b94e062cd900eb086919e5094003` (round-33 base
`cc46980359278d0967cf65e785b41c27b8d9c36c`). Date 2026-10-24.
Target: draft an append-only correction for the round-32 filed report's
receipt-lineage contradiction; do not edit the filed report.

Read-only inputs (all observed directly, no re-runs of lane work):

- `/home/vgpnk/Projects/shokunin/.ufo/reports/round-32/kama.md`
  (fleet commit `1d9840bb5c30bdc7012ef20399956c1769a2a964`, author
  `kama-shokunin <kama@shokunin.local>`, sha256
  `0ac23a281bd3bb009a606ef6cb55d6533b55389d189dd1fbf283a43748941f64`,
  fleet porcelain clean).
- `corpus/lessons/round-32-verifier-spotcheck.md` (routed defect 1 and 4 text).
- `corpus/lessons/round-33.md` (correction row 1).
- Committed receipts `.ufo/waves/round-32/{c2r,c2}/…`, their bytes, and their
  adding commits (`git log --diff-filter=A`, `git show --stat`).

## Behavior

Compared the filed report's two lineage statements with the committed receipt
bytes and the immutable commit graph, then reduced the difference to a
per-receipt table of (measured/evaluated revision, first-carrying commit).
Nothing was executed against the lane; the only commands were read-only `git`
(`log`, `show`, `hash-object`, `status`), `grep`, `sha256sum`, and small
`python3` reads of committed JSON/text. No file outside this report was written.

## Draft append-only correction (ready to append)

```markdown
### Round 33 — receipt-lineage erratum, per-receipt commits (routed defect 1, extension)

Superseded statement — filed `.ufo/reports/round-32/kama.md:99–101`, fleet commit
`1d9840bb5c30bdc7012ef20399956c1769a2a964`, sha256 `0ac23a28…8941f64`; bytes kept
unchanged:

> Receipt lineage honesty: `c2r/c2r-tip.json` and the gate/selftest finals measure
> the data tip `967d88528c1d` and are committed in `3f1a7330`; SCORECARD cites the
> data tip `c4c46ad5b87d` for the row revisions (ancestor of the tip).

Corrected per receipt (paths under `.ufo/waves/round-32/`):

| Receipt | Revision it measures/evaluates, and where that is recorded | Commit that first carries it |
|---|---|---|
| `c2r/c2r-tip.json` | `dc4258bdb08d658f1c5b15abc8378461659bd155` — JSON field `"tip"`; summary suffix `… met True tip dc4258bdb08d` | `967d88528c1d83535563f971863f7855f76b4849` |
| `c2/gate-data-tip.out` (intermediate, red) | `dc4258bdb08d…` — `defective .ufo/waves/round-32/count-c2r.py: missing-path:.ufo/waves/round-32/c2r/c2r-tip.json` (that receipt path did not exist at `dc4258bd`) | `967d88528c1d83535563f971863f7855f76b4849` |
| `c2/selftest-data-tip.out` (intermediate, red) | `dc4258bdb08d…` — `FAIL lane-tip dc4258bdb08d: exit=1 … GATE_SELFTEST pass=5 fail=1` | `967d88528c1d83535563f971863f7855f76b4849` |
| `c2/gate-tip.out` (final, green) | `967d88528c1d83535563f971863f7855f76b4849` — carried by the adding commit's message; the file itself holds only `registered 10 unregistered 0 defective 0` (no inline revision, no `EXIT_CODE`) | `3f1a73308bec9c2f4497c557d01bc58ec8e72eca` |
| `c2/selftest-final.out` (final, green) | `967d88528c1d83535563f971863f7855f76b4849` — inline `PASS lane-tip 967d88528c1d: exit=0 …`; `GATE_SELFTEST pass=6 fail=0` | `3f1a73308bec9c2f4497c557d01bc58ec8e72eca` |

So the `c2r` measurement revision is `dc4258bd…` and its receipt commit is
`967d8852…`; the `967d8852…` evaluated revision and the `3f1a7330…` receipt commit
belong to the final gate/selftest pair only. The sentence's SCORECARD clause
(data tip `c4c46ad5b87d` for the row revisions) is unaffected — `SCORECARD.md:1790`
does cite `c4c46ad5b87d` as the data tip, and it is an ancestor of every later
receipt revision.

Second pointer, same conflation — filed `.ufo/reports/round-32/kama.md:75–76`:

> After, data tip `967d88528c1d` (re-run of the `dc4258bd` measurement, receipt
> `c2r/c2r-tip.json`)

No committed count-c2r receipt records `tip` = `967d8852…` (JSON scan of
`.ufo/waves/round-32` and `.ufo/waves/round-33` for `tip`/`evaluated`/`revision`
fields: 0 hits; only `c2/selftest-final.out` names `967d8852…` in text). The
cited receipt is the `dc4258bd` evaluation; the after counts coincide at both
revisions (the non-author spot-check re-ran `967d8852` and matched every field
except `tip`), but count coincidence is not revision evidence.

This entry extends, and does not contradict, the round-33 append at
`SCORECARD.md:1850–1859`: that append's two facts are confirmed here (c2r `tip`
`dc4258bd…`, added `967d8852…`; finals `967d8852…`, added `3f1a7330…`). The
additions are the intermediate red pair, the `gate-tip.out` no-inline-revision
limit, and the `:75–76` pointer. Round-33 `KAMA_GATE_RECEIPT_V1` replays
(`.ufo/waves/round-33/c2/final/`, `SOURCE_REV=EVALUATED_REV=967d8852…`,
`EXIT_CODE=0`) supply the missing inline fields on new bytes; the round-32 bytes
are not altered.
```

## Evidence (commands and observed output)

| Check | Command | Observed |
|---|---|---|
| Filed bytes immutable | `sha256sum .ufo/reports/round-32/kama.md`; `git -C /home/vgpnk/Projects/shokunin status --porcelain -- .ufo/reports/round-32/kama.md` | `0ac23a28…8941f64`; porcelain empty; only commit `1d9840bb…` touches the path |
| Superseded sentence location | `nl -ba …/kama.md` | lines 99–101 (honesty bullet); lines 75–76 (C1 pointer) |
| c2r measured revision | `python3 -c` read of `c2r/c2r-tip.json` | `tip=dc4258bdb08d658f1c5b15abc8378461659bd155`; `base=07794a4d…` (counter constant, not a revision under test); `met True`, `valid 13`, `unresolved []` |
| c2r receipt commit | `git log --diff-filter=A --format='%H' -- .ufo/waves/round-32/c2r/c2r-tip.json` | `967d88528c1d83535563f971863f7855f76b4849` (sole commit touching the path) |
| Final pair commit | `git show --stat 3f1a7330…` | only `c2/gate-tip.out` and `c2/selftest-final.out`, +8 lines |
| Data-tip pair commit | `git show --stat 967d8852…` | includes `c2/gate-data-tip.out`, `c2/selftest-data-tip.out`, `c2r/c2r-tip.json`, four `kq36/*.json`, census end |
| Final selftest revision inline | `cat c2/selftest-final.out` | `PASS lane-tip 967d88528c1d: exit=0 …`; `GATE_SELFTEST pass=6 fail=0` |
| gate-tip self-containment | `cat c2/gate-tip.out` (41 B) | `registered 10 unregistered 0 defective 0` — no revision, no `EXIT_CODE` |
| Intermediate red bytes | `cat c2/gate-data-tip.out`, `c2/selftest-data-tip.out` | `defective … missing-path:…c2r/c2r-tip.json`; `FAIL lane-tip dc4258bdb08d … pass=5 fail=1` |
| No committed 967d8852 c2r receipt | Python JSON scan + `grep -rln 967d8852 .ufo/waves/round-32 --exclude=spec/validate/taskCall/run-render` | 0 JSON fields; only `c2/selftest-final.out` text |
| Byte pins used above | `sha256sum`; `git hash-object` | `c2r-tip.json` `d24caf0b…`/blob `b373d818…`; `gate-tip.out` `9acdd7cf…`/`131fd09d…`; `selftest-final.out` `6a9e009b…`/`7a3c75f4…`; `gate-data-tip.out` `98f55a2a…`/`6eada8d3…`; `selftest-data-tip.out` `c1c18960…`/`901f92e0…` |

Adjacent routed items observed while comparing (not this seat's deliverable, no
claim made): the three stale `*-v2.out` files are byte-identical to
`c2/before-base.out` (all sha256 `002a4b6072f54c8213b9914a1d8a15c5992907e8a26c7d685df5c6c519482a77`,
`registered 7 unregistered 2 defective 0`), while the genuine arms are
`thin-v2.out`, `noexit-v2.out`, `badpath-v2.out`; S193's quote sits at source
lines 15–16, 17 whitespace-delimited words; the round-33
`KAMA_GATE_RECEIPT_V1` files carry `SOURCE_REV`, `EVALUATED_REV`,
`EVALUATED_TREE`, `GATE_SHA256`, `RUNNER_SHA256`, `EXIT_CODE` and captured
streams. Sibling seats own those corrections.

## Gates

- Filed report: unmodified (sha256 above; fleet porcelain clean). No rewrite, no
  deletion, no relabel of the filed bytes.
- Lane mutations: none. No `git add/commit/push/stash/checkout/switch/reset/pull`,
  no jj mutation, no index write. Read-only `git` only.
- Scope: single file written — this report. No fleet-root or sibling write; no
  domain source tree touched.
- Tools: none installed or upgraded. Pacman not invoked (host-wide pause
  respected). No subagents spawned.
- No service restoration, endpoint readiness, model quality, or consumer-health
  claim is made; receipts cited are artifacts, not live serving evidence.

## Findings

1. The contradiction is confined to one receipt and one clause. The honesty
   bullet is true for the final gate/selftest pair (`967d8852`, carried by
   `3f1a7330`) and for the SCORECARD `c4c46ad5` citation; it is false for
   `c2r/c2r-tip.json` on both fields (measures `dc4258bd`, carried by
   `967d8852`).
2. The report's C1 after-measurement sentence (`:75–76`) points at the same
   `dc4258bd` receipt for a `967d8852` claim. No committed receipt supports a
   count-c2r evaluation at `967d8852`; the count identity is real but was
   established outside the lane by the non-author spot-check, not by committed
   bytes.
3. The intermediate red pair (`gate-data-tip.out`, `selftest-data-tip.out`,
   both `dc4258bd`, both in `967d8852`) is omitted from the honesty bullet; it
   is the receipt set that explains why the final pair is green at `967d8852`
   (the pinned c2r receipt path appears in `967d8852`).
4. `gate-tip.out` is not self-contained: no inline revision and no `EXIT_CODE`.
   Its `967d8852` attribution rests on the adding commit's message and on
   `selftest-final.out`. Any correction that says the final pair "records" the
   revision is precise only for the selftest file.
5. The existing `SCORECARD.md:1850–1859` append is correct but partial: it omits
   the `:75–76` pointer, the intermediate red pair, and the self-containment
   limit. The draft above is written to extend it without contradicting it, so
   the L1 can append as a new `###` block or fold the additions into a single
   erratum entry.

## Out of scope / not claimed

- Editing the filed report, SCORECARD, LOG, lessons, or SOURCES from this seat.
- Correcting the three stale `*-v2.out` files or the S193 quote (sibling seats).
- Re-running the counter or gate at `967d8852` to mint a new receipt; no such
  receipt is claimed to exist.
- Any judgment on whether the round-32 claims were met; the correction is a
  record-precision erratum only.

## Artifact paths

- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-33/w1/out/ScribeLineageErratum.md`
- Filed report (read-only): `/home/vgpnk/Projects/shokunin/.ufo/reports/round-32/kama.md`
- Receipts compared: `.ufo/waves/round-32/c2r/c2r-tip.json`,
  `.ufo/waves/round-32/c2/gate-tip.out`,
  `.ufo/waves/round-32/c2/selftest-final.out`,
  `.ufo/waves/round-32/c2/gate-data-tip.out`,
  `.ufo/waves/round-32/c2/selftest-data-tip.out`,
  `.ufo/waves/round-32/c2/before-base.out`,
  `.ufo/waves/round-32/c2/controls/{thin-row,empty-exit,nonexistent-path,thin,noexit,badpath}-v2.out`,
  `.ufo/waves/round-33/c2/final/` (replay receipts).
- Authority text compared: `corpus/lessons/round-32-verifier-spotcheck.md`,
  `corpus/lessons/round-33.md`, `SCORECARD.md:1790–1791,1826–1878`.
