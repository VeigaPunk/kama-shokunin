# ConnectSouji — souji ↔ kama overlap scan (r16 build wave)

Seat: connector, **read-only**, advisory only. Axis focus: **operability**, **calibration**.
Evidence base: `souji-shokunin/{SKILL.md,PROVINCE.md,corpus/QUALITY.md}`, one live read-only
`souji-verify.sh` run, `kama-shokunin/PROVINCE.md`, the r16 build `spec.json` context/C2 bullet,
and host artifact inspection (`ls`, `sha256sum`, `tar tzf`, `ldd`, `comm`, `df`, `findmnt`).
No kama gate/harness/test was executed; no install or upgrade was performed. Wrote only this file.

## 1. Contested scope

### A. `~/.cache/kama-shokunin/models/stories260K.gguf` (1,185,376 B, sha256 `270cba1b…d256d`)

| Claim | Evidence |
|---|---|
| Souji's title reaches "workspace hygiene" | `souji-shokunin/SKILL.md:5` (also `:2` description) |
| Its *surfaces* do not | `PROVINCE.md:21-23` lists only `$SHOKUNIN_ROOT`, lane repos, `origin` remotes — "GitHub remotes (`origin`) of the fleet and lane repos — read-only" |
| Its census cannot see it | `tools/souji-census.sh:16-17` scans "every immediate child of $SHOKUNIN_ROOT (or --root) whose .git is a directory"; a cache dir is never a row |
| Its probe cannot license it | live run today, exit 0: `NOT-SAFE none pushed=dirty-or-untracked-content; obsidian=no-matching-ledger-row; stale=not-scratch-type` |
| No receipt class can ever cover it | `pushed` needs an introducing commit (`SKILL.md:34`); `stale` needs a scratch family (`SKILL.md:50`); "Anything else, any doubt, any credential-shaped content" → `NOT-SAFE` (`SKILL.md:51`) |

Verdict: **unclaimed, not contested.** The title is broader than the tooling. kama must not read
"preserved artifact" in C2's context as a hygiene verdict; souji has no such receipt.

### B. `~/.local/opt/llama-b11755/` (51 files, 10 symlinks, 56,288,736 B) and `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 B, sha256 `753bfa73…e226`)

- Host/OS installs are refused: "souji removes files and never touches the OS" (`PROVINCE.md:43`);
  host operability is tsukuroi's (`PROVINCE.md:42`). Souji is artifact-only ("souji acts on artifacts
  and never on processes", `PROVINCE.md:40-41`).
- If ever claimed, the tarball is a **duplicate**, and duplicates are not core:
  "a `duplicate` receipt class would be a taxonomy change (operator decision)" (`PROVINCE.md:58-59`).
- Live probe on the tarball: `NOT-SAFE none`, same evidence string as A.
- Redundancy: every installed top-level name appears in the tarball listing (`comm -23` empty);
  the launcher member is byte-identical (`b6a31a8e…`). `SentinelInstallChain.md:9` measured the
  stronger form: "extracted tree == tarball, byte- and mode-exact".

Verdict: **hand off, do not absorb.**

### C. C2 teardown

Process teardown is outside souji entirely (`PROVINCE.md:40-41`). Not contested; kama owns the
teardown proof. C2 must not phrase teardown as workspace cleaning.

### D. The actual contest — the word "preserved" in C2

Neither lane defines it. Souji has no `preserved` receipt; kama has no lifecycle rule. Today the
only single digest covering **all** installed bytes is the tarball's `753bfa73…e226`, and that
tarball is exactly the artifact F3/operator may later remove; the planned receipt field
`server_sha256` is the 17,864 B launcher — 0.03 % of the 56.3 MB tree. "Preserved" is therefore
prose, not evidence. That gap is what the move in §4 closes.

## 2. What kama must hand off rather than absorb

1. **Tarball disposition** — souji integrator / operator (F3 taxonomy decision). C2 must not delete
   it. `SentinelInstallChain.md:70` already leaves retention open; this seat adds the reason a
   deletion is *irreversible for provenance* (§4).
2. **Any wording that C2 cleans or manages `~/.local/opt`** — tsukuroi/souji ground.
3. **A GC policy for `~/.cache/kama-shokunin/**`** — nobody owns it, and kama should not invent one
   this round. Its only legitimate interest is the pre-launch digest check it already has
   (`--model-sha256`, mismatch → exit 3).
4. **Souji's `NOT-SAFE` output as data, not a ruling** — certification is OFF
   (`SKILL.md:12`), so the live verdict is advisory evidence only.

## 3. Reusable conventions (and the live gaps they expose)

| Convention | Souji evidence | Use in kama r16 |
|---|---|---|
| Paired red/green arms against a frozen baseline, plus positive/dry-run controls | `QUALITY.md:43` — "must distinguish baseline from fixed bytes for the named operation-bound reason" | C1's frozen `93ee4302…cd64` vs repaired probe, with reject-all/loading-all controls, is this exact shape. Name both probe digests in the C1 report. |
| Digest the bytes actually measured; one writer per fragment | `QUALITY.md:30` — "names the sha256 of the bytes it measured, and that digest equals the installed file" | C1: hash the probe file actually invoked (not a copy); the ten `Matrix*` items already satisfy one-author-per-fragment. C2: §4. |
| Scratch under `/var/tmp` or lane-local, never `/tmp`; nothing new at repo root | `QUALITY.md:28`, `QUALITY.md:37`, and `census/round-12/connector.md:53` — "MUST use `/var/tmp/souji-r12-XXXXXX` or per-lane `$HOME/.cache/` with explicit trap cleanups" | C1 harness sets `KAMA_PROBE_TMPDIR=/var/tmp`; the probe already honours it (`tools/kama-probe.sh:1124`) and already traps cleanup (`:89`). |
| Before/after dependency state must agree | `QUALITY.md:49` (Q20) — "before/after dependency state must agree" | C2 server identity — the basis of the move. |

**Contradiction to record, not smooth:** `SentinelLiveSafety.md:123` says "Set `KAMA_PROBE_TMPDIR`
explicitly to the system tmp". On this host `/tmp` is a 128 G btrfs with 67 M inodes at 1 % used
(measured), so it is not a live hazard today — but the fleet record is the opposite
(`census/round-12/connector.md:53`: `/tmp` inode table 100 % full), and the probe scratch would then
follow a different volume policy from the matrix evidence. Prefer `/var/tmp`.

## 4. Move (one)

**Adopt souji's Q20 declared-dependency rule for C2's server identity: hash the resolved
llama-server install tree before spawn and after teardown, require the two maps equal, and make
that aggregate the receipt's identity anchor.**

Mechanics (additive; no new writes, no deletion):

- After `realpath(--server)`: `tree_dir = dirname(realpath)`; require a real directory (refuse a
  symlinked tree — the same refusal souji applies to digest scopes, `SKILL.md:35`).
- sha256 every depth-1 regular file (measured here: 51 files / 56,288,736 B; tens of ms) →
  `install_tree = {relpath: sha256}`, and `install_tree_sha256 = sha256` over `relpath\0sha256\n`.
- Repeat after teardown; receipt carries both maps, `install_tree_stable` (bool) and one
  `install_tree_sha256`. Unequal → non-zero exit with both maps retained.
- `tests/llamacpp-live/check-receipt.py` additionally requires
  `server_sha256 == install_tree[basename(realpath(server))]`, plus an optional
  `--expect-install-tree-sha256 HEX` for independent re-runs.

**Why this is not already covered.** Two digests in the context look like provenance:
asset `753bfa73…e226` (tarball) and the `--server` sha256 (launcher `b6a31a8e…`, 17,864 B).
The serving code is `libllama-server-impl.so` (7,671,544 B, `e404b91a…`) plus five further
`$ORIGIN`-resolved libraries — `libllama.so.0.7.0` (`983e1a2a…`), `libllama-common.so.0.7.0`
(`3270bc66…`), `libmtmd.so.0.7.0`, `libggml.so.0.27.0` (`8643a58b…`), `libggml-base.so.0.27.0` —
and the runtime-selected `libggml-cpu-*.so` variants, which are installed but not in the static
load set. The launcher digest pins 0.03 % of the tree; the
tarball digest pins all of it but is the artifact hygiene may remove. The tree map is the only
identity that both describes the executing bytes and survives a hygiene pass; Q20's equality makes
it tamper-evident for the run. This converges with `CriticC2ToyModel.md:45` ("also record the
sha256 of `libllama-server-impl.so`, `libllama.so.*` and `libggml*.so`") and adds the aggregate,
the gate cross-check, and the pre/post arm the critic did not name.

**Axis impact.** Calibration ↑: the receipt's identity claim becomes true of the install tree and
comparable across re-runs; a receipt mixing a foreign `server_sha256` with a b11755 tree is
rejected by the cross-check. Operability ↑: a swapped or partially extracted install fails loudly
instead of green-lighting an unknown server; cost is 2 × 56 MB of local hashing. Harm: none to C1,
none to C2's declared surfaces — no port change, no `~/.config`/`~/.omp`/systemd write, no deletion.

**Risks / contradictions.** (a) The receipt schema is shared with `LiveReceiptGate` (in flight):
keep the field additive/optional, or an already-accepted receipt becomes invalid; L1 decides
whether r16 requires it. (b) The map is *installed*, not *loaded*: llama.cpp picks one
`libggml-cpu-*.so` at runtime, so the map is a superset of executed bytes — wording must say
installed-tree (`QUALITY.md:57`, Q23). (c) TOCTOU: swap-and-restore between the two hashes is out
of reach; state it. (d) Cost bounds are host-specific: require a normal directory and fail closed
otherwise.

**Verification (L1 runs it, not this seat).**
1. `python3 -m py_compile tools/kama-llamacpp-live.py`, then one live run with `--out`.
2. Assert `install_tree_stable: true`, `install_tree_sha256` 64 hex,
   `install_tree["llama-server"] == server_sha256`,
   `install_tree["libllama-server-impl.so"] == e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`.
3. Negative arm: copy the tree, flip one byte of `libllama-server-impl.so` in the copy, run against
   the copy with `--expect-install-tree-sha256` set to the real tree's value → gate must reject.
   This is Q19's baseline-vs-fixed distinction (`QUALITY.md:43`) applied to artifacts.
4. Cross-check the asset: `sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` → `753bfa73…e226`.

## 5. Routed defects (not mine to fix)

1. `tools/kama-probe.sh:1124` — scratch defaults to `/tmp`. Low severity today (1 % inodes,
   125 G free, measured); C1's harness should export `KAMA_PROBE_TMPDIR=/var/tmp`. Contradicts
   `SentinelLiveSafety.md:123`; prefer `/var/tmp` per `QUALITY.md:28` and
   `census/round-12/connector.md:53`.
2. C2's context pairs "asset sha256 753bfa73…" with the installed binary. The asset digest is the
   tarball, not the server; keep the two names distinct in the final report or a reader will take
   the tarball digest as the served-code digest.
3. Tarball as an F3 candidate row: 22,240,468 B, sha256 `753bfa73…e226`, installed name-set
   covered; no receipt class exists today (`PROVINCE.md:58-59`). Decision belongs to the operator.
4. `~/.cache/kama-shokunin/**` has no owner for eventual removal. Do not add GC logic to kama; keep
   the digest precondition only.

## 6. Limitations

- Read-only seat. The only lane tool executed was souji's own read-only probe (exit 0); everything
  else was `ls`/`sha256sum`/`tar tzf`/`ldd`/`comm`/`df`/`findmnt`.
- Per-member byte equality of the whole tarball was not re-measured here; I verified name-set
  coverage plus the `llama-server` member, and rely on `SentinelInstallChain.md:9` for the
  byte-and-mode-exact claim.
- Souji's deletion certification is OFF (`SKILL.md:12`); its verdicts are used as advisory data.
- No install/upgrade performed.
