# J5Preload — round 53, C1 ablation control (code from outside the tree)

**Verdict: the ablation trips the frozen instrument only for non-root code — an extra
user-owned library outside the unpacked tree gives `code=0` (plus replay mismatch
`code-mapping:foreign:…:uid=1000`), but the same extra library made *root-owned and not
writable* passes untouched (`code=1`, `met=True`, `own_code.verified true`), so C1's stated
type ("the code the server executes is the archive's own bytes") is not enforced for uid 0.**

Scratch: `/fast/scratch/hyaku/kama-r53/J5Preload` (clone, fixture commits, receipts), removed
after the artifacts were copied. Counter used: the lane file
`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py`,
`sha256 = 1a7a1442…b75d8f`, i.e. exactly the preregistration's `counter_sha256`. The lane
working tree currently carries in-flight L1 edits (`git status`: `M tools/kama-live-replay.py`,
`M tools/kama-llamacpp-live.py`); the counter does not read them — it measures `git archive`
of the tip it is given, and every run below measured a commit of my own clone.

## Fixture (my `git clone --shared`, commits made there with `-c user.name=fx -c user.email=fx@invalid`)

| variant | commit | what the live child's server loads |
|---|---|---|
| parent (build) | `c22602bd8d83ab26349d1087e916ca537ee4f9d1` | nothing extra |
| v1 | `fbafd3c810a502c57dfbecf23bab8f6f6bd25be2` | `LD_PRELOAD=<TMPDIR>/kama-preload/libggml-rpc.so`, a **uid-1000** copy of the tree's own member, outside the tree |
| v2 | `662a30105e71a5280286a0d6019d1adf22ea4765` | the same bytes at `/usr/local/lib/kama-r53/ggml/libggml-rpc.so`, **root-owned 0644** |
| v3 | `23d1eb54bb8c9bb03aeb531a52b244770d696679` | `/usr/local/lib/kama-r53/ggml/libkama-ablate.so`, **root-owned 0644**, a library the archive never shipped (compiled for this control: `int kama_r53_ablate(int x){return x+1;}`, 15 264 B, sha256 `ed00835019db5a80725e854e9a618bff1c05da08e4ca67c898ef9ffb9d7d48b6`) |

The tool change is minimal and honest to the lane's shapes: inside the existing
`if args.server_fd is not None:` branch, after `child_env['LD_LIBRARY_PATH'] = …`
(`tools/kama-llamacpp-live.py:2150` at the build), set one more child env name
`child_env['LD_PRELOAD']`; because `receipt['child_env_keys'] = sorted(child_env)`, the
fixture also admits the name in `tests/llamacpp-live/check-receipt.py`
(`CHILD_ENV_FD_MODE`, line 69, and its diagnostic string) so the receipt stays a valid lane
receipt. Patches: `control.patch` (v1), `control-foreign.patch` (cumulative to v3).

```
python3 tools/round53-replay-code-audit.py --repo $S/lane --tip <commit> --scratch <dir> --out <file>
```

## v1 — user-owned code from outside the tree (the assigned ablation): caught

`c1-ablation-user-owned.out`, exit 1:

```
tip=fbafd3c810a502c57dfbecf23bab8f6f6bd25be2
bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=0/3 met=False
detail: code b1: code: executable mapping /fast/…/run/r53c1-jqbfcfxr/work-b1/tmp/kama-preload/libggml-rpc.so (103:05 2095783703) is neither an archive file under the unpacked tree nor a root-owned host file (uid 1000, 103:05 2095783703, writable True)
detail: bind b1: replay exit 1 match False refused None
```

The same line repeats for `b2` and `b3` (per-run inode 1957325796, 279199440). The counter's
own `/proc/<pid>/mem` witness is what fails, i.e. C1's `code` leg is independent for uid != 0.

Replay, run directly on the fixture (`replay-user-owned.json`, exit 1):

```
replay match=False refused=None mismatches=1 exit=1
match False refused None live_exit 0
mismatches:
  code-mapping:foreign:/fast/…/rw/tmp/kama-preload/libggml-rpc.so:uid=1000
own_code verified False
members ['llama-b11909/libggml-base.so.0.27.0', 'llama-b11909/libggml-cpu-zen4.so', 'llama-b11909/libggml-rpc.so', 'llama-b11909/libggml.so.0.27.0', 'llama-b11909/libllama-common.so.0.7.0', 'llama-b11909/libllama-server-impl.so', 'llama-b11909/libllama.so.0.7.0', 'llama-b11909/libmtmd.so.0.7.0']
host ['/usr/lib/ld-linux-x86-64.so.2', … 13 root-owned host libs …]
mapping count 22
```

`code-mapping:foreign` is exactly the mismatch the ticket asked about, and it is the only
one: the foreign library is recorded in `code_mappings` with `opened: true`, `uid: 1000`.
The lane's own checker accepts the fixture's rerun receipt, so the ablation is a configured
product, not a broken receipt: `python3 tests/llamacpp-live/check-receipt.py $S/rw/rerun-receipt.json`
→ `VALID …` exit 0 (`check-receipt-user-owned.txt`); `child_env_keys ['HOME','LANG','LD_LIBRARY_PATH','LD_PRELOAD','PATH','TMPDIR']`,
`outcome pass`.

## v2 / v3 — the same code, root-owned: not caught at all

`c1-ablation-root-owned.out` (v2), exit 0:

```
tip=662a30105e71a5280286a0d6019d1adf22ea4765
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
detail: code b1: 8 archive files (8 executable ranges) byte-equal … , 14 root-owned host files; …
```

14 host files, not 13: the extra one is the preloaded copy. `c1-ablation-foreign-archive.out`
(v3) is identical in shape — `bind=1 sealed=1 code=1 teardown=1 newrow=1 … met=True`, exit 0,
`14 root-owned host files` — although the extra library is **not any archive member**.
Replay on v3 (`replay-foreign-archive.json`, exit 0):

```
match True mismatches [] live_exit 0
own_code verified True members 8
hosts: … /usr/lib/libzstd.so.1.5.7, /usr/local/lib/kama-r53/ggml/libkama-ablate.so
ablate mapping entry: [{'dev': '00:1e', 'inode': '120099668', 'opened': True, 'path': '/usr/local/lib/kama-r53/ggml/libkama-ablate.so', 'sha256': 'ed008350…48b6', 'size': 15264, 'uid': 0}]
```

The server executed 15 264 bytes of code the release never shipped, and both witnesses
reported a clean run with `own_code.verified true`.

## Findings

**F1 — measured, positive.** For code outside the tree owned by a non-root user, the
control works: `code=0` from the counter's own reading of `/proc/<pid>/mem`/`maps`
(`round53-replay-code-audit.py:443-452`) and `code-mapping:foreign` from the replay
(`kama-live-replay.py:332-333` at `c22602bd`). C1's acquisition boundary holds there.

**F2 — defect (primary).** `"root-owned" is not provenance.`
- `tools/round53-replay-code-audit.py:452` — `host.add(path)`: a non-tree executable mapping
  is accepted once `st_uid == 0`, inode matches and it is not writable; nothing relates it to
  the archive or to any pinned name/digest.
- `tools/kama-live-replay.py:332-335` (build `c22602bd`) — `elif e.get("uid") != 0: …foreign…`
  `else: host.append(path)`: same rule, and `verified = not probs`, so such a rerun is a
  *match*.
- Reproduce: v3 above (`--tip 23d1eb54…`) → `met=True`; or directly
  `python3 tools/kama-live-replay.py --receipt .ufo/waves/round-48/c2/live/receipt-1.json --work $S/rw3 --out out.json`
  → `match True`, `mismatches []`, the foreign path inside `own_code.host`.
- Why it matters for the claim: `preregistration.json` C1 `type` reads "the code the
  witnessed replay's server executes - not only its launcher image - is the release
  archive's own bytes, observed by the counter in the server's memory against its own
  download of the archive". The predicate behind it admits any root-owned host file, so the
  measured statement is weaker than the claim: a root-owned `LD_PRELOAD` (or any
  root-installed library on the loader path) executes with the *archive's* libraries still
  verified, and both witnesses stay green. Planting needs root, which bounds the threat, but
  the witness no longer says what the claim says it says.
- Proposed fix (`proposed-round54-host-pin.diff`, against the frozen counter, compiles):
  pin the 13 host libraries the build observed by **path and sha256** (`HOST_LIBS`), and in
  the non-tree branch require `HOST_LIBS[path] == sha_file(path)`, else
  `code: executable mapping … is outside the unpacked tree and is not one of the 13 pinned
  host libraries`. Measured both ways with the proposal in my out dir:
  - `c1-proposed-foreign.out` (v3): `bind=1 sealed=1 code=0 teardown=1 newrow=1 … met=False`
    exit 1, detail `code b1: code: executable mapping /usr/local/lib/kama-r53/ggml/libkama-ablate.so is outside the unpacked tree and is not one of the 13 pinned host libraries`;
  - `c1-proposed-build.out` (`--tip c22602bd…`, no ablation): `bind=1 sealed=1 code=1
    teardown=1 newrow=1 … met=True` exit 0 — no false positive on the build.
  Residual risk stated plainly: the pin is this host's Arch/b11909 library set; a host library
  upgrade moves those digests, so the pin must be re-frozen deliberately (which is the point).

**F3 — diagnostic defect (minor).** `tools/round53-replay-code-audit.py:623` (`om = {}`) folds
"own_code is merely unverified" into every member comparison, so one real mismatch prints as
one real line plus eight fake `code: replay own_code.members['…'] None != archive digest`
lines (see `c1-ablation-user-owned.out`); a reader cannot tell which members were actually
verified. Fix: keep `om = oc.get("members") if isinstance(oc.get("members"), dict) else {}`
and guard the member loop with `oc.get("verified") is True`.

**F4 — leg coupling (minor, records a property, not a bug to patch silently).**
`tools/round53-replay-code-audit.py:591` adds the replay's `exit/match` to `probs`, i.e. the
`bind` leg. In v1 a *code-only* failure therefore also reports `bind=0` and `bound=0/3`: the
leg tuple cannot distinguish "the replay refused on the foreign mapping" from "the bind leg
broke". The proposal run at v3 shows the separation when the replay itself stays green
(`bind=1` + `code=0`). Either give the replay refusal its own leg, or say in the claim that
`bind` subsumes the replay verdict.

## Host hygiene

- Root-owned fixture files were placed only under `/usr/local/lib/kama-r53/ggml/`
  (never a PATH directory): `sudo -n cp … && sudo -n chmod 0644` — and removed:
  `sudo -n rm -rf /usr/local/lib/kama-r53` → verified absent (`ROOT-LIB-REMOVED`).
- No pacman, no installs (nothing was needed) — nothing to record in a tool ledger.
- Servers: every run I started was reaped by the counter/replay; `pgrep -af llama-server`
  shows only another seat's held server under `/fast/scratch/hyaku/kama-r53/K2Design/…`,
  which is not mine and was left alone.
- The lane, fleet and shokuknow trees were read-only throughout; no lane file was edited, no
  jj/Git mutation outside my clone; `$S` removed after the artifacts were copied.

## Artifacts (all under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J5Preload/`)

`c1-ablation-user-owned.out` (v1 counter), `replay-user-owned.json` (v1 replay),
`check-receipt-user-owned.txt`, `c1-ablation-root-owned.out` (v2), `c1-ablation-foreign-archive.out`
(v3), `replay-foreign-archive.json` (v3 replay), `c1-proposed-foreign.out`,
`c1-proposed-build.out`, `control.patch`, `control-foreign.patch`,
`proposed-round54-host-pin.diff`, `fixture-commits.txt`, `SHA256SUMS`.
