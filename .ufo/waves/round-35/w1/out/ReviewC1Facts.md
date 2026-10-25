# ReviewC1Facts

Recommendation: treat C1's four committed-byte facts as re-derived. Do not treat the stronger readings below as re-derived. No lane or fleet object was mutated. No tool was installed.

Judged axis: calibration. MISSION.md:29 still says operability + freshness; this seat did not edit it and did not change the C1 predicate.

Canonical runtimes are two separate git repositories. `git -C /home/vgpnk/Projects/shokunin rev-parse --show-toplevel` is `/home/vgpnk/Projects/shokunin`. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` is the lane. The fleet report blob `7610d532696f5c6e214840fa2ec4112584589252` is not an object in the lane database, and the lane README/manifest blobs are not objects in the fleet database. Same-identity was checked inside each repo: `git cat-file -p <blob>` equals `git show <rev>:<path>` for all four blobs (byte lengths 16816, 35771, 15309, 7131).

## Findings by severity

### High

None. Each counter conjunction in `tools/round35-statement-audit.py` `facts()` re-derives from the pinned `git show`.

### Medium

None.

### Low

1. The label "live-seat sentence" does not re-derive from the fleet report. `16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` contains `2 seats` 0 times and `seats still live` 0 times. It contains `2 lane processes still live` once, line 103. The spot-check paraphrase `2 seats still live` is only in `corpus/lessons/round-34-verifier-spotcheck.md` line 96 at `719655f12517a9ce6b1a5ca44316897fed8420b0`. Confirm the process sentence. Do not cite the paraphrase as the report's words. The counter's token is the process sentence, so this does not falsify `R34-LIVE`.

## Commands and counts

Fleet report (exit 0, 16816 bytes, 244 lines). Blob `git -C /home/vgpnk/Projects/shokunin rev-parse 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` = `7610d532696f5c6e214840fa2ec4112584589252` (matches the pin in the counter).

```
git -C /home/vgpnk/Projects/shokunin show 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md
```

| needle | count |
| --- | ---: |
| `coverage map gains two entries` | 1 |
| `22 untracked` | 1 |
| `2 lane processes still live` | 1 |
| `dispatch-manifest.json` | 1 |
| `Cannot combine --prompt with --auto` | 1 |
| `2 seats` | 0 |

`git -C /home/vgpnk/Projects/shokunin grep -c -F` on that rev for the first three needles each printed `:1`.

Lane README (exit 0, blob `df71357b4605858a014f90c08ca2c5fedb8f1a45`, 35771 bytes). Same blob at `29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007`, `b784e1ab273472eaa750fc10918ca4be67fa7697`, and `719655f12517a9ce6b1a5ca44316897fed8420b0`.

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md
```

| needle | count | whitespace-collapsed count |
| --- | ---: | ---: |
| `serving-alias-contract.md` | 0 | 0 |
| `served-model-id-resolution.md` | 0 | 0 |
| `## Coverage map — round 34` | 0 |  |
| `## Coverage map — round 35 addition` | 0 |  |
| `coverage map gains two entries` | 0 |  |

Near-miss map rows are present and do not satisfy the needles: `knowledge/served-model-identity.md`, `knowledge/alias-endpoint-normalization.md`, `knowledge/served-identity-crosswalk.md`. Coverage-map headings present: round base, round 10, round 11, round 29, round 31.

Lane spot-check (exit 0, blob `2888879c06d6bd4667219148e13c99e95abcba5f`, 15309 bytes). Introduced by `719655f` (`round-34 verifier spot-check (integrator, hyaku): non-author admit/reject`, 2026-10-24 21:09:20 -0300).

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/lessons/round-34-verifier-spotcheck.md
```

| needle | count |
| --- | ---: |
| `23 untracked` | 2 |
| `1 modified` | 1 |
| `Do not carry that live count forward` | 1 |
| `2 lane processes still live` | 1 |
| `22 untracked` | 2 |

Committed manifest (exit 0, blob `b32113564fd019bfaa60d14511abd91d080cfe74`, 7131 bytes, no trailing newline). Same blob at `719655f`. `b784e1ab273472eaa750fc10918ca4be67fa7697` is an ancestor of `719655f`. No commit between them changes this path.

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show b784e1ab273472eaa750fc10918ca4be67fa7697:.ufo/waves/round-34/w1/out/dispatch-manifest.json
```

| needle | count | whitespace-collapsed count |
| --- | ---: | ---: |
| `Cannot combine --prompt with --auto` | 0 | 0 |
| `--auto` | 0 |  |
| `--prompt` | 0 |  |
| `auto` (case-insensitive) | 0 |  |
| `prompt` | 1 |  |

The one `prompt` hit is the transport string `kimi --agent ufo-<role> -p <prompt> ...`, not `--prompt`. Parsed JSON keys are `wave`, `dispatchedAt`, `transport`, `seats`. Seat count 33, unique names 33, no `note` key, `dispatchedAt` `2026-10-24T20:37:01-0300`. `git grep -c -F 'Cannot combine --prompt with --auto' b784e1ab273472eaa750fc10918ca4be67fa7697 -- .ufo/waves/round-34/w1/out/dispatch-manifest.json` exited 1 with empty stdout.

Wrong-repo control: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 719655f12517a9ce6b1a5ca44316897fed8420b0:.ufo/reports/round-34/kama.md` exited 128 (`path does not exist`). The map sentence cannot be re-derived from the lane repo alone.

## The four facts

### R34-MAP — re-derived

Report lines 185–188:

```
- Frontier rows advanced: none of the lane's own frontier rows changed ground. The
  coverage map gains two entries on the served-name/alias theme
  (`corpus/knowledge/serving-alias-contract.md`,
  `corpus/knowledge/served-model-id-resolution.md`).
```

README at `719655f` does not name either file. The counter conjunction holds: report has the sentence, README lacks both names.

Bound, not a failed fact: the knowledge files exist at that tip. `git cat-file -s 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/knowledge/serving-alias-contract.md` = 4009; `served-model-id-resolution.md` = 2828. They were added by `29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007` (ancestor of `719655f`) without a README change (`git show --stat` on that commit lists only those two knowledge files). The false claim is the coverage-map sentence, not "the entries are absent from the tree."

### R34-R33COUNT — re-derived

Report lines 113–115, phrase contiguous on line 114:

```
The round-33 wave ran **after** the round-33 report was filed (its registry carries
`createdAt 2026-10-24T06:52:20Z`, `updatedAt 07:42:46Z`) and left 22 untracked
outputs under `.ufo/waves/round-33/w1/out/`.
```

Spot-check line 82: `plus 23 untracked outputs` and `the report says 22 untracked; this count is 23`. Line 95, the only `1 modified` hit: `Report says 22 untracked round-33 outputs; porcelain shows 23 untracked plus 1 modified registry.` Both `23 untracked` hits are the round-33 leftover claim. The counter conjunction holds.

Bound: this re-derives the spot-check's committed sentences. It does not re-count porcelain at report time. That recount is outside this seat.

### R34-LIVE — re-derived as a process sentence, not a seat sentence

Report line 103: `` `.ufo/waves/round-34/w1/out/`; 2 lane processes still live. ``

Spot-check line 77 quotes that process sentence and says it is not supported by seat-log mtimes. Line 96 says `Do not carry that live count forward` (count 1) and paraphrases the claim as `2 seats still live`. The counter conjunction holds: report has the process sentence, spot-check has the do-not-carry sentence.

Bound: these blobs do not contain a pid table. Historical liveness is not re-derived here. See the low finding for the seat/process wording.

### R34-MANIFEST — absence re-derived for the committed blob only

Report line 105 is the only `dispatch-manifest.json` hit. The citation is line-wrapped, so a same-line search for the error phrase next to the filename fails:

```
104|attempt died at spawn for all 33 seats with `error: Cannot combine --prompt with
105|--auto.`; it is recorded in `.ufo/waves/round-34/w1/out/dispatch-manifest.json`.
```

Collapsed, that is one claim that the error is recorded in the manifest. The contiguous phrase `Cannot combine --prompt with --auto` occurs once in the report, on line 41 (mistakes list), which does not itself name the manifest. Wrapped form `Cannot combine --prompt with\n--auto` also occurs once (lines 104–105).

The committed manifest lacks the phrase, lacks `--auto`, and lacks a note field. The counter conjunction holds.

Attack on the wrong object: the working tree file is dirty (`git diff --numstat` = `70 36` for `.ufo/waves/round-34/w1/out/dispatch-manifest.json`, 8086 bytes) and contains the phrase once, on line 271, inside a `note` field. `--auto` occurs twice there. Absence is true of blob `b32113564fd019bfaa60d14511abd91d080cfe74` and false of the uncommitted file. This seat did not stage or edit that file.

## Residual risk and verification gaps

- Porcelain count of 23 and the modified-registry count were not re-measured from `git status`. Only the spot-check sentences at `719655f` were re-derived.
- Process liveness at 20:56 was not re-measured. The spot-check's mtime and pid claims are not in the four shown blobs.
- A correction row that says the two knowledge entries do not exist would be false at `719655f`. The re-derived fact is only that README does not name them.
- A correction row that says the committed manifest contains the error sentence would be false. A row that says the working tree lacks it would also be false.
- Naive `grep` for a single line containing both the error phrase and `dispatch-manifest.json` in the fleet report returns no line. The citation re-derives only if lines 104–105 are joined.
- Report blob identity was re-checked after the shows and still equals `7610d532696f5c6e214840fa2ec4112584589252`. No resume path and no continuity preflight were in this seat's scope; no git index or jj state was touched.
