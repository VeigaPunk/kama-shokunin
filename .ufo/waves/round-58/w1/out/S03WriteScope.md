# S03WriteScope — round-58 write-scope census (kama, w1)

Leaf seat, read-only intent: no lane/jj/git mutation, no campaign tool run, scratch `S=/fast/scratch/hyaku/kama-r58/S03WriteScope` removed after copying receipts.
Snapshots: A `16:54:15`, B `16:58:19`, C `16:59:42`, D `17:01:51` (the tree moved during the audit: the L1 landed `8188dbb2` at `16:58:18` and kept editing after it).
Revs: base `2f53614e`, freeze `dcd69473`, controls `cb1ef102`, build tip `e4891d8a`, lane HEAD at A/B `e4f207f5`, at C `8188dbb2`.

## Method (exact checks, all exit 0)
- `git -C <lane> status --porcelain=v1 -uall | grep -v '\.ufo/waves/round-58/'` and `git -C /home/vgpnk/Projects/shokunin status --porcelain=v1 -uall` → `lane-status-*.txt`, `fleet-status.txt`.
- Porcelain cannot see ignored writes or content-identical rewrites, so: `find <lane> -name .git -prune -o -name .jj -prune -o -path <lane>/.ufo/waves/round-58 -prune -o -type f -newermt '2026-10-27 16:50:00' -printf '%TH:%TM:%TS %p\n'` → `mtime-outside-58.txt`; `git check-ignore -v`; wt-vs-`git show HEAD:` sha256 → `inplace-rewrites.txt`, `measured-restoration.txt`.
- Provenance: `stat` mtimes, `.jj` file mtimes, `git log --format='%h %ci %s'`, X07's own `lane-status-before.txt`.

## In-bound inventory (allowed)
- Lane B: 362 porcelain paths, 358 of them `w1/out/<Seat>/…` plus L1 markers `w1.ready`, `w1.ready.dispatched` (the earlier `w1.ready.partial` disappeared between calls — L1 dispatch state, inside the wave dir).
- Lane C: 386 paths, all but 4 under `.ufo/waves/round-58/`. Lane D: 442 paths, 435 in-bound; the 7 outside are the L1's in-flight closure edits ` M SCORECARD.md` (`16:59:44`), ` M corpus/QUALITY.md` (`17:01:22`), ` M corpus/SOURCES.md` (`17:00:34`), ` M corpus/lessons/round-58.md` (`17:01:22`) plus the three pre-wave strays below. L1 writes, not seat writes — but a gate that only reads `.ufo/waves/round-58/` would miss or wrongly credit them.
- Fleet: 4 paths at B, 5 at D (below).

## W1 — HIGH — tracked round-56 measured receipts rewritten by an unharnessed battery run
- At A/B: ` M .ufo/waves/round-56/measured/{base-c1,build-c1,m-drop-ldaudit,m-drop-ldaudit-target-fails}.out`; `git diff` is pid-only churn (`2361912→2532595`, `2361914→2532600`, `2361916→2532602`, `2361918→2532604`), all four written `16:51:52.758–16:51:53.051` (verbatim diff: `measured-churn-1654.diff`).
- Exploit path: `tools/round56-env-leg-battery.py:11` hardcodes `OUT = LANE/".ufo/waves/round-56/measured"`; `main()` writes five receipts there. Any unharnessed `python3 …round56-env-leg-battery.py` (or a copy whose `LANE` is not patched) rewrites tracked lane evidence. Fifth receipt `comparator-selftest.out` is deterministic, so it changed content-neutrally but kept mtime `16:51:52.660` — a persistent trace after restoration.
- Attribution: one battery `main()` (4 writes 100 ms apart). Not X07: its `lane-status-before.txt:1-4` (16:53:32) already lists the 4 `M` entries and its `patched.diff` moves `LANE`/`OUT` to `$S`. No w1 report claims the run; the frozen counter/checker mask `Path.write_text`, so the run bypassed both. Author not determinable from local bytes.
- State at C: restored in place `16:59:23.524–.527`; all four sha256 == `HEAD` blob and porcelain clean (`measured-restoration.txt`). Impact was ~7 min of mutated evidence, not a counter defect: C1 reads blobs at `--tip`.
- Smallest remediation: point `OUT` at `$TMPDIR` (or take it from argv) and have any "real legs" reproduction patch `LANE` (X07 pattern); a restore must be recorded as a lane write.

## W2 — HIGH — the frozen "hermetic harness" does not confine writes (still true at `8188dbb2`)
- `tools/round58-battery-exec-check.py:104-106` masks only `Path.write_text/write_bytes/mkdir` (+ `Popen`, `os.system`, `TemporaryDirectory`); `Path.open("w")`/`os.open` are unmasked. Docstring line 12 ("nothing is written, nothing is run") is false.
- Proof, scratch-only (`harness-escape.txt`): fixture battery with `Path(p).open("w")` + `Path(q).write_text` + `os.open/os.write`, run as `TMPDIR=$S python3 <lane>/tools/round58-battery-exec-check.py --repo $S/harness-test/pathopen --tip HEAD --work $S/harness-test/scratch-pathopen` → rc 1, `met=False`; `pathopen.txt` PRESENT, `osopen.txt` PRESENT, `writetext.txt` ABSENT. Control: the genuine variant with `LANE` patched to `$S/fake-lane` → rc 0 `met=True`, zero files written (mask works for `write_text`).
- Independently and more broadly found by S01 (`F3`: builtin `open`, `os.makedirs`, `shutil.copy`, `os.remove`, `ctypes` exec, real `os.posix_spawn`, reading `/etc/hostname`); its markers went to `/home/vgpnk/kama-r58-S01-escape/` (now absent). `8188dbb2` added nonce/expect-binding but kept the same mask list.
- Impact: C1 grades untrusted committed candidate code with real write (and read/exec) authority; a candidate can rewrite `SCORECARD.md`, `corpus/`, or these very receipts while being "evaluated". Bounded to what C1 certifies, not to the frozen kill rule.
- Smallest remediation: run the harness child under `bwrap`/`unshare` with the lane read-only and scratch the only writable mount (S01 R3), or an `addaudithook` deny-list for `open`/`os.*` write modes.

## W3 — MEDIUM — committed variant set hardcodes absolute LANE and a cross-round shared scratch
- All 16 `tests/round58-battery-variants/*.py` keep `OUT = LANE / ".ufo/waves/round-56/measured"` (line 11) and `scratch = pathlib.Path("/fast/scratch/hyaku/kama-r56/l1-battery")` (r56, not r58, not per-seat). Unharnessed variants therefore write lane evidence and share one mutant path — two concurrent seats collide.
- Smallest remediation: derive both paths from `TMPDIR`/argv in `make-variants.py` and regenerate the set.

## W4 — LOW — writes invisible to a porcelain-only gate
- `tools/__pycache__/round58-c1-counter.cpython-314.pyc` created `16:51:39` (ignored by `.gitignore:3`) — a lane write outside any seat dir, absent from `git status`.
- `corpus/SOURCES.md` `16:54:45`, `corpus/lessons/round-58.md` `16:55:13`, `tools/round58-battery-exec-check.py` `16:58:12` were written in place while `git status` still read clean (then-HEAD `e4f207f5`); the same three land changed in `8188dbb2` (`+2` rows, `+35` lines, `+31` lines) — L1 integration writes, legal for the L1 but invisible to the ticket's instrument for ~4 min.
- Read-side effect, self-reported: a `git status` sweep refreshes `.git/index` (`chousa-shokunin/.git/index` `16:55:45` matches my sweep; `GIT_OPTIONAL_LOCKS=0 git status` there shows only `?? .ufo/waves/round-59/`, no tracked change). Lane index `16:51:58`. Use `git --no-optional-locks` for audits.

## W5 — MEDIUM — blocked-fetch artifact left in the fleet root
- `?? /home/vgpnk/Projects/shokunin/o.bin`, `5867` B, `16:58:36` (inside the wave window), `file` = "HTML document… Cloudflare", `<title>Just a moment...</title>`, only `challenges.cloudflare.com` referenced. No w1 report mentions `o.bin`.
- Impact: an out-of-bound write from the fleet-root cwd; secondarily a provenance hazard — a challenge page is not source content, so any citation of an origin fetched at `16:58:36` must be reopened. Smallest remediation: `curl -o "$S/…"` (never bare redirect) and delete the artifact.

## Out-of-bound but pre-wave (not round-58 seat writes)
- `?? .ufo/scopes/kama-r57-w1/swarm-registry.json` (`15:05`, `"wave": "kama-r57-w1"`) — round-57 registry written into the lane instead of the wave tree.
- `?? .ufo/waves/round-57/ClaimFalsifier/09/fixtures/fixtureA|B/` (`15:08–15:11`, 280 K) — nested git repos (`git -C … rev-parse --show-toplevel` returns the fixture paths; one commit each) left inside the lane tree.
- Fleet: ` M .ufo/reports/round-58/chousa.md` (`15:04`, +10 lines after commit `3c429f59`), `?? .scratch/closure-mado-r50.json` (`06:38`), `?? .scratch/source-routing-queue.md` (`14:40`), `?? .ufo/waves/round-75/w1/RevEntryQuality.md` (`14:07`) — none under `.ufo/waves/round-58/`, none in the wave window.
- Sibling-lane scan (read-only, `GIT_OPTIONAL_LOCKS=0`): no round-58 residue; `kotodama-shokunin` has `round-75/assimilation/validate/corpus/lessons/round-58-*.md` (its own round), `chousa-shokunin` has `?? .ufo/waves/round-59/`.

## Position on the frozen kill rule
Nothing here alters the frozen C1/C2 predicates or the 11 enumerated variants. W1 rewrites evidence, not the counter; W2/W3 limit what C1's harness certifies (S01's F1–F5 sharpen the same seam); W4/W5 are audit-instrument defects, not claim credit.

## Limits
- W1/W5 attribution is temporal + mechanism + exclusion of the one seat that documented a patched run; no process-level owner survives, and no seat reported either write.
- Counts are point-in-time; the wave was still writing at C (386 lane paths) and `SCORECARD.md` was modified in place by the L1 at C.
- I read no agent transcripts and executed no lane or campaign tool; the only programs I ran were `git`/`find`/`stat`/`sha256sum` reads and the frozen checker against fixtures in `$S`.

Receipts: `.ufo/waves/round-58/w1/out/S03WriteScope/` — `lane-status-outside-58.txt`, `fleet-status.txt`, `measured-churn-1654.diff`, `measured-restoration.txt`, `harness-escape.txt` (+`pathopen.txt`, `osopen.txt`), `mtime-outside-58.txt`, `inplace-rewrites.txt`, `o-bin.txt`.
