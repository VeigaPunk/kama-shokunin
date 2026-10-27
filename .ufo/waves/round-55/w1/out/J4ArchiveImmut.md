# J4ArchiveImmut — round-55 w1 (lane kama): C1 archive-reference immutability probe

**VERDICT — no falsification.** C1's archive-reference immutability holds: the counter's
reference is one in-memory read of its own download taken at
`tools/round54-replay-code-audit.py:920`, *before the first replay exists*, and every
member comparison is served from that `io.BytesIO` blob; a same-uid replay that reaches
`<S>/counter-archive.tar.gz` and overwrites it **in place (same inode)**, renames it,
forges attacker bytes at the path and finally deletes it changes **no** member
comparison (measured `met=True … code=1 … exit 0`). Only a vanish *before* that read
fails the run, and it fails **closed** (`met=False`, `exit 1`).

Frozen bytes verified in every probe: `tools/round54-replay-code-audit.py`
sha256 `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`
(= prereg `claims.C1.counter_sha256`). Nothing frozen was edited; the fixtures are
commits in a throwaway `git clone --shared` of the lane.

## 1. Path relationship (read from `start_replay`/`bind_one`/`prepare_env`)

| step | file:line | fact |
|---|---|---|
| counter scratch | `round54-replay-code-audit.py:885,887` | `root = a.scratch`; `S = tempfile.mkdtemp(prefix="r53c1-", dir=root)` |
| reference path | `:915` | `apath = os.path.join(S, "counter-archive.tar.gz")` |
| download write | `:918-919` | `open(apath, "wb")` + `shutil.copyfileobj` |
| **one read** | `:920` | `arc = Archive(apath)` → `self.blob = fh.read()`, `tarfile.open(fileobj=io.BytesIO(self.blob))` (`:451-453`); the `with open(...)` closes the fd |
| digest | `:921` | `hashlib.sha256(arc.blob)` — **the same bytes that are parsed**, not the file |
| replay env | `:613,616` | `prepare_env` sets `TMPDIR = S/tmp-<tag>` |
| replay launch | `:633-641` | `cwd=tree`, `env=prepare_env(...)`; argv carries `--work S/work-<tag>` (`:635`), `--out S/<tag>.json` (`:637`), `--witness-dir S/wd-<tag>` (`:635`) |
| first replay | `:936` | `bind_one(...)` — **after** `:920` |

So `dirname(TMPDIR) == dirname(--work) == dirname(--out) == S`: the replay has four
independent handles on the directory that holds the reference (measured in
`evidence/attack-evidence.jsonl`, `scratch_S` / `apath` fields). Unit probe
`archive-ref-probe.py` confirms the layout and permissions: file mode `0o644`, owner
uid 1000 = the replay's uid, `S` mode `0o700` owned by that same uid → **the file is
reachable and writable from the replay side**. The defence is not permissions.

## 2. The attack, executed end-to-end (two fixtures)

Both fixtures patch only `tools/kama-live-replay.py` (the replay the counter extracts
from `--tip`) to locate `S` via `dirname($TMPDIR)` and act on the reference; the
counter, preregistration and controls were not touched.

| run | fixture tip | replay action on `<S>/counter-archive.tar.gz` | counter verdict |
|---|---|---|---|
| control | `9c60eae6` (frozen build tip) | none | `met=True`, **exit 0** (`evidence/control-at-tip2.out`; matches `.ufo/waves/round-55/measured/c1-build.out`) |
| A | `2e486c1e` | b1: rename original aside + write a **forged 22 MB tar.gz** at the reference path (attacker bytes in `llama-b11909/libggml-base.so.0.27.0`); b2: **unlink** the path; b3/kill: observe | `met=True`, `code=1`, **exit 0** (`evidence/attack-forge-vanish.out`) |
| B | `f4d26a15` | b1: **in-place overwrite of the same inode** with the forged tar.gz (the Sen1Mem F1 shape), then rename + forge at the path; b2: **unlink**; b3/kill: observe | `met=True`, `code=1`, **exit 0** (`evidence/attack-inplace-forge2.out`, rc file `…=0`) |

Fixture B's own evidence (`evidence/attack-inplace-forge2.evidence.jsonl`):

```json
{"leg":"b1","action":"inplace+forge","exists_before":true,
 "sha256_before":"bf94332a…e695b","before_is_frozen_release":true,
 "inode_before":1282220685,"same_inode_inplace":true,"sha256_after_inplace":"59fd1a7d…",
 "forged_members_swapped":["llama-b11909/libggml-base.so.0.27.0"],
 "forge_differs_from_release":true,"inode_after_forge":…}
{"leg":"b2","action":"vanish","vanished":true,"exists_after":false}
{"leg":"b3","exists_before":false} {"leg":"kill","exists_before":false}
```

i.e. at the instant of the counter's two `/proc/<pid>/mem` passes the reference **path
held a forged archive with attacker member bytes (and its original inode had been
overwritten in place with them)**; the counter still reported the honest 8 members /
16 ranges "byte-equal … to the counter's own archive", `twopass=3/3`, `rehash=0`,
`met=True`. Nothing the replay can do to that file reaches the comparison.

## 3. What the counter does if the archive vanishes

**(a) After the read (the only case a replay can cause): nothing.** `Archive` holds
`self.blob` and the tarfile over `io.BytesIO(self.blob)` (`:451-453`); `member()`
(`:456-464`) never touches the path. Measured: fixture A/B legs b2/b3/kill deleted or
found the file absent and the run finished `met=True`, `exit 0`.

**(b) Before the read (concurrent same-uid process, not the replay): fails closed.**
`Archive(apath)` raises `FileNotFoundError` (an `OSError`) → caught by
`except (OSError, tarfile.TarError)` at `:926-927` → detail
`counter archive unavailable: FileNotFoundError: …` → `arc` stays `None` (`:914`) →
`bind_one` `:718-719` appends `code: the counter has no archive of its own` for each of
b1–b3 → `code=0`, `hostlibs=0/3`, `twopass=0/3` → `met=False` → `return 0 if met else 1`
(`:966`) → **exit 1**. Measured end-to-end by unlinking the file while the counter was
downloading it (`evidence/vanish-before-read4.out`, rc file `= 1`):

```
bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3
envnames=3/3 hostlibs=0/3 anon=0 twopass=0/3 rehash=0 met=False
detail: counter archive unavailable: FileNotFoundError: [Errno 2] No such file or directory:
        '…/scratch7/r53c1-h9a37zm4/counter-archive.tar.gz'
detail: code b1: code: the counter has no archive of its own        (b2, b3 likewise)
```

## 4. Why a tamper cannot launder (counterfactual, offline)

`forge-counterfactual.py` (`evidence/forge-counterfactual.out`) drives the frozen
`Archive` and a verbatim reconstruction of the pre-fix class
(`.ufo/waves/round-53/w1/out/Sen1Mem/c1-reference-immutability.diff`):

* **(A) in-place overwrite, same inode** (`inode before/after 335554960 / 335554960`):
  frozen `member()` → `REAL-RELEASE-MEMBER-BYTES` (release), `sha256(arc.blob)` still
  the release digest; pre-fix lazy class → `!!ATTACKER-MEMBER-BYTES!!`.
  → the F1 exposure was real for a path/fd-based reference, and the read-once snapshot
  is what closes it.
* **(B) rename-over + forged file at the path (new inode)**: inert for *both* (the
  frozen class snapshotted; the pre-fix fd still points at the old inode).
* **(3) `Archive(path)` again after the tamper** → attacker bytes. That is the only
  shape that would launder the swap, and the frozen counter never performs it: `apath`
  occurs at lines **915, 918, 920 only** (`grep -n apath tools/round54-replay-code-audit.py`).

Fixture B additionally shows shape (A) end-to-end on the real 22 MB archive, not just
in a fixture tar.

## 5. Residual notes (no defect found; nothing here falsifies C1)

1. **The reference file stays replay-reachable and writable** for the whole run; only
   the *compared bytes* are immutable. The `Archive` docstring (`:445-448`) says the
   replay "cannot rewrite the reference" — true of the bytes, not of the file. Suggest
   wording "cannot change the bytes it compares".
2. **No leg re-stats or re-hashes `apath` after the replay**; a tampered file would go
   unreported. Inert for the verdict (the blob is authoritative) and `S` is
   `shutil.rmtree`'d (`:968`), so nothing leaks into the receipt — but any future edit
   that re-reads the reference (e.g. a closing re-hash) would silently reopen F1.
   Advisory, not applied: `fixtures/advisory-unlink-reference.diff` (`os.unlink(apath)`
   right after the digest check; no behaviour change).
3. **Pre-read TOCTOU** (`:918-920`) is reachable only by a concurrent same-uid process,
   not by the replay (which starts at `:936`); it fails closed (digest mismatch or
   `FileNotFoundError` → `met=False`). DoS at most, never a false green.
4. The prereg's C1 `limits` do not mention that the reference *file* is
   replay-writable; the counter's own docstring does. A one-line disclosure would make
   the limit set complete.
5. Adjacent, same shape (not a falsification): the model reference
   `S/counter-model.gguf` (`:901`) is read once into `vocab` at `:910`, before any
   replay; the model's *mapped* bytes are checked from the replay's own file via
   `mapped_model` (`:362-392`), not from the counter's copy.

## 6. Commands (scratch `S=/fast/scratch/hyaku/kama-r55/w1/J4ArchiveImmut`, clone at `$S/lane`)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane        # read-only source
git -C $S/lane rev-parse --show-toplevel                                      # -> $S/lane
python3 tools/round54-replay-code-audit.py --repo $S/lane --tip <commit> \
        --scratch $S/scratchN --out out/J4ArchiveImmut/evidence/<name>.out     # + `echo $? > rc`
python3 $S/archive-ref-probe.py      out/J4ArchiveImmut/evidence/archive-ref-probe.out
python3 $S/forge-counterfactual.py   out/J4ArchiveImmut/evidence/forge-counterfactual.out
python3 $S/make-fixture.py $S/lane   out/J4ArchiveImmut/evidence/attack-evidence.jsonl   # fixture 1
git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -am "j4 fixture: …"       # 2e486c1e
python3 $S/vanish-watcher.py $S/scratchN out/J4ArchiveImmut/evidence/<log> 300           # vanish-before-read
```

No tool was installed or upgraded (no pacman, no uv, no binaries); the counter needs
only python3 + network. No llama-server process was left behind
(`pgrep -af llama-server` → 0 after the runs; the counter's teardown leg reaps its own).
Scratch (`$S`) was removed after the receipts were copied into this directory.

## 7. Files written (all under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/`)

* `J4ArchiveImmut.md` (this report)
* `J4ArchiveImmut/archive-ref-probe.py`, `forge-counterfactual.py`, `make-fixture.py`,
  `vanish-watcher.py`, `run-counter.sh`
* `J4ArchiveImmut/fixtures/fixture1-attack-patch.diff` (rename+forge+vanish),
  `fixtures/fixture2-attack-patch.diff` (in-place overwrite+forge+vanish),
  `fixtures/advisory-unlink-reference.diff` (advisory, not applied)
* `J4ArchiveImmut/evidence/`: `control-at-tip2.out` (+`-at-tip.out`), `attack-forge-vanish.out`,
  `attack-inplace-forge.out`, `attack-inplace-forge2.out`, `vanish-before-read{,-2,-4}.out`
  + `vanish-before-read4.watcher.log`, `archive-ref-probe.out`, `forge-counterfactual.out`,
  `attack-evidence.jsonl`, `attack-evidence2.jsonl`, `attack-inplace-forge2.evidence.jsonl`.
