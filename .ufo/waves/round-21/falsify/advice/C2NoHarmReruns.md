VERDICT: confirm - all 11 nh-*/fr-* exits and stream contents reproduce at b76727f in a fresh clone; 3 raw sha256 mismatches flagged, each caused only by an embedded clone path or a random mkdtemp name; none substantive.

Target attacked: recorded exit and stdout/stderr sha256 of the 9 nh-* and 2 fr-* items in runs/b76727f3/commands.json, re-run from recipe.json in a fresh clone (master=b76727f, clean). Lane untouched.

Method (all exit 0 unless noted):
- `git clone --no-hardlinks` then `checkout -B master b76727f...`; `status --porcelain` empty.
- jq-filtered recipe (11 items) run via `/usr/bin/python3 <clone>/.ufo/waves/round-21/run.py --recipe ... --out ...`: run 1, run 2 (same clone), and attacked tip a661714 (second clone).
- `falsify/out/C2NoHarmReruns/compare.sh` x3; `crosscheck.py` (independent Python JSON parse).

| item | exit (rec=rerun) | stdout sha256 | stderr sha256 | class |
|---|---|---|---|---|
| nh-error-pair | 0=0 | match | match | exact |
| nh-error-selftest | 0=0 | match | match | exact |
| nh-install-tree-grid-selftest | 0=0 | match | match | exact |
| nh-gguf-selftest | 0=0 | match | match | exact |
| nh-gguf-measure | 0=0 | MISMATCH | match | path: 11 lines embed clone path; equal after path normalization |
| nh-citation | 0=0 | MISMATCH | match | path: 17 lines embed clone path; equal after path normalization |
| nh-citation-selftest | 0=0 | match | MISMATCH | stderr embeds random mkdtemp dir; equal after suffix normalization; can never match raw |
| nh-sources-append-only | 0=0 | match | match | exact (`--to` = b76727f in this clone) |
| nh-snapshot-selftest | 0=0 | match | match | exact |
| fr-sources-validate | 0=0 | match | match | exact; clone-rooted run exact after root-path normalization |
| fr-sources-census | 0=0 | match | match | exact; clone-rooted run exact after root-path normalization |

Findings (severity order):
1. [low, attestation] Raw hashes are not portable across paths or time: 2 stdout streams embed absolute lane paths and 1 stderr embeds a random mkdtemp name, so 3/11 raw hashes cannot match a re-run in another clone. Record normalized hashes, or drop stderr hashing for nh-citation-selftest.
2. [low, reproducibility] fr-* argv pins the live fleet root, not the lane, so they read the live working tree and fleet inputs that recipe.json does not pin: scripts/sources-census.sh (sha256 3fb72615..., mtime 2026-10-19 21:22 -0300) and shokunin.conf (sha256 bfdf96c4..., mtime 2026-10-19 21:10 -0300). Both predate the official run (2026-10-21 11:14 UTC) [INFERENCE: unchanged since measurement].
3. [low, date] validate's E08 check uses `date -u` (sources-census.sh:661); the recipe passes no --today. No E08 finding today; a future-dated `opened` row would change the result.
4. [info, working tree] citation-provenance.py reads SCORECARD.md, LOG.md and corpus docs from the working tree (lines 33-34, 59). The live lane has an uncommitted SCORECARD.md edit; copying it into the clone left nh-citation output byte-identical (evidence/cit-live-scorecard.out = evidence/cit-committed.out). Live reruns are not committed-state reruns.
5. [info] The live lane has uncommitted edits to tools/report-landing-audit.py (C1 detector) and SCORECARD.md. Live-tree references to report-landing-audit are docs, the errata registry and one tools/__pycache__ .pyc; no executed in-scope script or spawned child references it. a661714 vs b76727f: 86 added files, all under runs/b76727f3/ (evidence/diff-b76727f-a661714.txt); its rerun gives 11/11 exits and the same 3 flagged items.
6. [info] nh-gguf-measure reads host-external /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf (present); it reproduces on this host only.

Controls (executed): run 2 equals run 1 on every stream except the mkdtemp stderr; recorded raw streams equal recorded JSON hashes; recorded exit equals expected for all 28 items; recipe placeholders substitute to the recorded argv for all 11 (evidence/recipe-substituted.tsv vs recorded-argv.tsv); clone tree stays empty under `status --porcelain --ignored`.

Gaps: C1/C2 claims, census-before (rows 65) and c1-/c2- items not re-measured (out of scope); gguf model sha not independently checked (measure.py compares size and sha256 to its pinned oracle, lines 615-616, so exit 0 implies a match); lane clean state at measurement is [INFERENCE] from run.py's start-only check.

Tools and disclosure: no installs or updates. Observed: Python 3.14.8 (/usr/bin/python3), git 2.56.0, GNU Awk 5.4.1, bash 5.3.20; `jq` on PATH is jaq 3.1.1, used only for JSON extraction and cross-checked by Python. `git status` ran 2-3 times against the live lane without GIT_OPTIONAL_LOCKS=0 (may refresh the index stat cache; no content change intended). `python3 -m http.server 8765` (pid 1047871) predates this seat and was left alone.

Evidence: .ufo/waves/round-21/falsify/out/C2NoHarmReruns/ (compare.sh, compare-*.txt, crosscheck.py, crosscheck.txt, evidence/).
