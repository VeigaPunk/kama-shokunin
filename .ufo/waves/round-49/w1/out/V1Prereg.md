# V1Prereg — round-49 freeze integrity (lane kama)

**Verdict: PASS — all six freeze-integrity checks hold on the frozen preregistration at 36d5ed2681111b68c180f8ab1646d8dc9beaedee.**

Scoped to seat item V1Prereg; no defect found. No tools installed (nothing to record per tooling directive). Lane read-only; all reads via `git show`/`git log` on the scratch shared clone (`/fast/scratch/hyaku/kama-r49/V1Prereg/lane`, `git clone --shared` of the lane; clone HEAD `122c4ee9` == lane working-tree HEAD).

## 1. Preregistration predicate sentences == PREDICATE sentences in both counters' docstrings — PASS

Method: extracted each counter's docstring `PREDICATE (same sentence in the preregistration):` block from `git show 36d5ed26:<counter>`, normalized whitespace (regex `\s+`→single space), compared to `claims[i].predicate` of `.ufo/waves/round-49/preregistration.json`. Both normalized strings byte-equal.

- C1: preregitation.json:17 vs tools/round49-replay-witness-audit.py:65-72 → **MATCH**
- C2: preregistration.json:30 vs tools/round49-append-audit-v4-check.py:62-66 → **MATCH**

Exact normalized C1 predicate: `a replay of each of the three committed v5 b11909 receipts holds its rerun server up for an outside observer, which finds the frozen llama-server binary executing as the listener of the announced port with the frozen model, round-trips a fresh nonce through /tokenize and /detokenize against the model's own vocabulary, and sees the server gone after release; the live tool refuses a sparse or size-mismatched archive member before hashing it; and the tokenize surface is a source row; witness=1 cap=1 newrow=1.`
Exact normalized C2 predicate: `append-only-audit at the measured commit grades dated text laundered through an exempt heading, refuses substring, negated and wildcard self-declaration bindings, keeps the native head carve-out, and on the lane binds every contract row, exits 0 and ungrades no deleted line whose origin is not an exempt section; fixture=1 lane=1.`

## 2. counter_sha256 == `git show 36d5ed26:<path> | sha256sum` — PASS

| counter | preregistration.json counter_sha256 | `git show 36d5ed26:… \| sha256sum` |
|---|---|---|
| tools/round49-replay-witness-audit.py | `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` (json:19) | `86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1` |
| tools/round49-append-audit-v4-check.py | `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` (json:32) | `26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945` |

## 3. Both counters byte-identical at 74558c71c38ceaeace15fd4cf8aa9d84977584b1 — PASS

`sha256sum` of both counters at 74558c71 equals the frozen digests above (and the same at HEAD `122c4ee9` and in the lane working tree, `sha256sum` of the working files):

```
86b4a40d…  tools/round49-replay-witness-audit.py   (freeze 36d5ed26 / build 74558c71 / HEAD / working tree)
26c465a9…  tools/round49-append-audit-v4-check.py   (same four)
```

## 4. freeze/prereg-time-check.out consistent with prereg-time-check.py run — PASS

Ran `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/prereg-time-check.py --repo $S/lane --path .ufo/waves/round-49/preregistration.json --rev 36d5ed2681111b68c180f8ab1646d8dc9beaedee`; stdout captured to `prereg-time-check.run.out` (copied to out dir), exit=0. `diff` with `.ufo/waves/round-49/freeze/prereg-time-check.out` → **IDENTICAL** (byte-for-byte, including the `exit=0` trailer):

```
rev=36d5ed2681111b68c180f8ab1646d8dc9beaedee path=.ufo/waves/round-49/preregistration.json
committer_time=2026-10-26T20:18:04-03:00 max_future=86400
  ok   line 6: 2026-10-26T23:17:45Z (at/before commit)
RESULT pass: no timestamp later than the committer time
exit=0
```

## 5. frozen_at_utc precedes the freeze commit time — PASS

- preregistration.json:6 `frozen_at_utc = 2026-10-26T23:17:45Z`.
- Freeze commit `git log -1 --format='%H %cI' 36d5ed26` → `36d5ed26 … 2026-10-26T20:18:04-03:00` (= 23:18:04Z UTC).
- 23:17:45Z precedes 23:18:04Z by **19 s** (assertion in Python passed). Also consistent with the `.out` line ` ok line 6 … (at/before commit)`.

## 6. Build paths absent at 36d5ed2681111b68c180f8ab1646d8dc9beaedee — PASS

At the freeze commit (files exist there; `git cat-file -e 36d5ed26:<path>` ok for all four), no occurrence of any build marker:

| build path | probe at 36d5ed26 | result |
|---|---|---|
| witness flag (replay) | `git show 36d5ed26:tools/kama-live-replay.py \| grep -n witness` | no matches (rc=1) |
| hold_for_witness (live) | `git show 36d5ed26:tools/kama-llamacpp-live.py \| grep -n 'hold_for_witness\|witness'` | no matches (rc=1) |
| v4 tool | `git show 36d5ed26:tools/append-only-audit.py \| grep -n '"definition"\|v4'` | no matches (rc=1) |
| S494/S495 | `git show 36d5ed26:corpus/SOURCES.md \| grep -n 'S494\|S495'` | no matches (rc=1) |

Positive control — the build commit introduces exactly these paths: `git diff --stat 36d5ed26 74558c71` = `corpus/SOURCES.md (+2)`, `tools/append-only-audit.py (+101/-…)`, `tools/kama-live-replay.py (+27/-…)`, `tools/kama-llamacpp-live.py (+151/-…)`; at 74558c71 the replay contains 17 `witness` hits, the live tool 2 `hold_for_witness` hits, append-only-audit.py docstring declares `"definition": "v4"` (lines 2,4,6,219), and SOURCES.md has S494 at :247 and S495 at :248. The freeze-vs-base diff (`438127bc → 36d5ed26`) touches only counters, preregistration, controls, census, and the two source captures (`.ufo/waves/round-49/c1/proc_pid_exe.5.txt`, `server-README-caa8191d.md`), i.e. nothing outside freeze scope.

## Residual risk / verification gaps

- None in scope. Counters, preregistration and controls were not executed/modified (frozen per instructions; not this seat's item). The known integration items (counters not yet in SKILL.md instrument registry; SCORECARD/LOG/lesson/QUALITY/README round-49 entries; S494/S495 used-by pointing at corpus/lessons/round-49.md) are explicitly out of scope for this leaf seat.
- Evidence receipts: copied `prereg-time-check.run.out` to out dir; scratch removed.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Prereg.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V1Prereg/prereg-time-check.run.out`
