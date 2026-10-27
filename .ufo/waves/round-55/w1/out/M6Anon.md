VERDICT: C1 anon-leg mutation probe complete — 4 of 5 weakening mutants survive the honest-build detector at 9c60eae6 (met=True, expected), the 5th (x-filter drop) is killed by over-flagging (met=False); the synthetic-maps unit harness kills all 5; no defect found in the counter.

# Scope

Round 55 item M6Anon (kama C1, operability): mutate the anonymous-mapping
classification in `tools/round54-replay-code-audit.py` `code_observe`
(lines 494–513 at sha256 c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af,
matching `.ufo/waves/round-55/preregistration.json` claims.C1.counter_sha256).
Two detectors per mutant:

1. repo-level: run the mutant at build tip `9c60eae6f7ed84f7da93d219a406aadc30958c6c`
   against a `--shared` clone of the lane (`git clone --shared` under scratch;
   counter invoked read-only with `--repo <clone>`).
2. unit-level: `harness.py` imports each module with importlib and feeds
   `code_observe(pid, tree, arc, probs, collect=True, own)` a hand-written
   `/proc/<pid>/maps` (module-level `open` shadow for the maps path; `os` shim
   whose `open` returns a real `memfd_create` fd for `/proc/<pid>/mem` and whose
   `pread` serves fixture bytes).

Mutations are in scratch copies only; the frozen counter was never edited.

# Mutation points (each = smallest behavior-bearing edit; diffs in mutants/*.diff)

| mutant | site | edit |
|---|---|---|
| m1-anon-append | tools/round54-replay-code-audit.py:505 | `probs.append("code: anonymous executable mapping …")` deleted; `continue` retained → every non-`/` exec row skipped silently |
| m2-memfd-name | :511-512 | `if own is None or (dev,ino) != own: probs.append(…)` deleted; `continue` retained → any `/memfd:` row admitted by name alone |
| m3-kernel-maps | :144 | `KERNEL_MAPS` widened with `"[jitbuf]"` → an exec row with that bracketed name is skipped as a kernel mapping |
| m4-xperm | :496 | `or "x" not in f[1]` dropped → non-executable rows are classified as executable |
| m5-nopath-skip | :498 | `len(f) < 6` split out to `continue` → a maps row with no pathname field is skippable (bracketed names still flagged) |

Mutant sha256s (of `mutants/*.py`): pristine c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af
(identical to the frozen counter), m1 38346fb83eef6ea878f04a3e13fd47fbf6845abafca19070563a42f4abf47c5d,
m2 d202007479e6d2aadb492dbca62b46187d9614a6d1986c3ed1a83168082c33cc,
m3 58f196b22c9bdaeb998eecd8a509f7d4b1d18432bcf3a86d62595a4bdcd334f6,
m4 8c1f1b813e3e35a424c30ae17d7fb6b678c78d0ed7a9a8861a7d794452f23b97,
m5 2b0208ff3fc4b50448a3e3c1c01f1e62f03bfdffc33d449a4b9c826405f84f53.

# Repo-level detector (tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c)

Command per mutant:
`python3 mut/<mutant>.py --repo <shared clone> --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --scratch <per-mutant dir> --out <receipt>`

Pristine baseline (frozen measurement, copied: `c1-build.baseline.out`):
`bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True`, exit 0.

| mutant | exit | summary line vs baseline | verdict |
|---|---|---|---|
| m1-anon-append | 0 | byte-identical (met=True) | SURVIVED |
| m2-memfd-name | 0 | byte-identical (met=True) | SURVIVED |
| m3-kernel-maps | 0 | byte-identical (met=True) | SURVIVED |
| m4-xperm | 1 | `code=0 coderuns=0/3 hostlibs=0/3 anon=490 met=False` | KILLED |
| m5-nopath-skip | 0 | byte-identical (met=True) | SURVIVED |

m1/m2/m3/m5 survive as expected: the honest server has no anonymous exec page,
no foreign memfd, and no made-up bracket name, so weakening the leg is invisible
on an honest build — consistent with preregistration target text and with the
kill battery's reason for existing.

m4 is killed by the same detector: with the `x` filter dropped, the honest
server's non-executable anonymous rows become "anonymous executable mapping"
problems (490 in the clean run; the count varies with pid/maps layout, the kind
is stable). Sample detail lines from `m4-xperm.full`:
- `code: anonymous executable mapping 56282ae9b000-… rw-p (name '[heap]')`
- `code: anonymous executable mapping 7f2ef0000000-… rw-p (name '(none)')`
- `code: anonymous executable mapping 7f2ef0021000-… ---p (name '(none)')`
plus follow-on noise (`code: root-owned host library /etc/ld.so.cache is not in
the frozen host set`; the uid-1000 model file now "neither … nor a root-owned
host file"). So m4 is an over-flagging mutant and the honest build catches it —
`met=False`, exit 1, receipt `m4-xperm.out`.

Note on run hygiene: the first m4 attempt was SIGKILLed by my own 1500 s
watchdog *after* printing its verdict — its ~65 KB of output had filled the
stdout pipe (65536-byte artifact observed). Rerun with output streamed to file:
exit 1, 16 s, receipt written. No llama-server or replay process of this seat
remains (`pgrep -af M6Anon` empty; `pgrep -af llama-server` shows only other
seats' processes).

# Unit-level detector (harness.py, synthetic maps fixture)

Fixture rows (all at fake pid 424242; `own=("00:2b","9999")`):
- 4 exec rows under `/fx/tree` whose bytes match FakeArc members (admitted: compared 4 ranges)
- `r-xp /usr/lib/libc.so.6` real root-owned host lib (admitted: host=1)
- `r-xp /memfd:llama-server (deleted)` at 00:2b/9999 = own (admitted: sealed image)
- `rwxp` anonymous exec page, no pathname (K1Cheat shellcode shape)
- `r-xp /memfd:foreign (deleted)` at 00:2a/4242 ≠ own (foreign exec memfd)
- `r-xp [jitbuf]` made-up bracketed name
- `rw-p` anonymous NON-executable page, no pathname
- `r-xp [vdso]` real kernel mapping (skipped by all)

Pristine flags exactly the three planted bad rows:
```
code: anonymous executable mapping 7f0000100000-7f0000108000 rwxp (name '(none)')
code: executable memfd /memfd:foreign (deleted) (00:2a 4242) is not the sealed image
code: anonymous executable mapping 7f0000300000-7f000030800 r-xp (name '[jitbuf]')
```
and nothing else (`out: files=4 host=1 ranges=4 snaps=4`). Both required classes
(anonymous exec, foreign memfd) are flagged — the pristine leg works.

| mutant | unit verdict | mishandled row |
|---|---|---|
| m1-anon-append | KILLED | rwxp anonymous row and `[jitbuf]` row silently skipped (only foreign memfd still flagged) |
| m2-memfd-name | KILLED | foreign `/memfd:` admitted by name; flag lost |
| m3-kernel-maps | KILLED | `[jitbuf]` exec row skipped as kernel mapping; flag lost |
| m4-xperm | KILLED | `rw-p` anonymous row newly flagged as "anonymous executable mapping" |
| m5-nopath-skip | KILLED | 5-field rwxp row (no pathname) skipped; flag lost, `[jitbuf]` still flagged |

Every mutant changed `code_observe`'s verdict on the fixture — all 5 KILLED by
the unit detector. Full transcript: `unit-harness.out`.

# Verdicts

- repo-level @9c60eae6: m1 SURVIVED, m2 SURVIVED, m3 SURVIVED, m4 KILLED (over-flagging), m5 SURVIVED.
- unit-level synthetic maps: all 5 KILLED.
- The four survivors are weakening mutants invisible on an honest build: the
  counter's classification code is only exercised under attack, so the kill
  battery (m-ldaudit-foreign vector et al.) is the necessary detector — the
  survivors here are expected, not coverage findings.
- m4's repo kill is informative: the `x` filter is load-bearing for the honest
  build (every process has non-exec anonymous maps), so it cannot be removed
  silently — the counter defends that boundary in both directions (missing exec
  flagging weakens; extra flagging is honest-build-visible).
- No defect in the frozen counter: classification, the own-memfd admission, the
  KERNEL_MAPS list, the `x` filter and the no-pathname handling all behaved to
  spec under both detectors.

# Environment / tools

- python3 (system), git clone --shared for the lane; no installs needed, no
  pacman transactions. Counter sha256 re-verified:
  `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`.
- Lane accessed read-only via the shared clone; fleet repo untouched; no fixture
  commits were needed (the probe feeds maps via the harness instead).

# Files

Out dir `.ufo/waves/round-55/w1/out/M6Anon/`:
- `mutants/pristine.py` (frozen counter copy), `m1..m5 *.py` + `*.diff`
- `harness.py`, `unit-harness.out` (unit detector transcript)
- `m*.out` (repo-level `--out` receipts), `m*.full` (stdout+stderr)
- `c1-build.baseline.out`, `base.c1.control.out` (copied frozen references)

Report: .ufo/waves/round-55/w1/out/M6Anon.md
