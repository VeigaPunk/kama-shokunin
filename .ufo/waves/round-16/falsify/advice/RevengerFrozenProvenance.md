VERDICT: confirm — the frozen-probe chain (manifest.json ↔ git blob 20e392e:tools/kama-probe.sh ↔ snapshot bytes ↔ run-before.json's probe_sha256) is byte-exact at every link, and the manifest is load-bearing in measure.py's gate rather than documentation.

# What was attacked

The provenance of `.ufo/waves/round-16/frozen/kama-probe-before.sh` as the *pre-round-16* probe used for C1's red arm: that `frozen/manifest.json` describes it truthfully, that the git object it names produces those same bytes, that the snapshot is those bytes, and that `run-before.json` attributes its numbers to them. Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`, lane commit `b8e485cc6b201c8e4604a20808e58babbfe08e34`.

# The chain, link by link

Expected digest `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` throughout.

**1. manifest.json is internally true.** `sha256sum .ufo/waves/round-16/frozen/*` → exit 0; snapshot `93ee4302…cd64`, manifest `f76b472b…d579`. Manifest field set is exactly `{snapshot, sha256, source_commit, source_path, source_blob, capture, bytes}` with `sha256=93ee4302…cd64`, `bytes=47443`, `source_commit=20e392ea683a36bc223eb7cb45897acfb45456a3`, `source_blob=447e29b397405a3ee9813ca2e44aedf88abe2763`, `capture="git show 20e392e:tools/kama-probe.sh"`.

**2. The named commit and blob exist and are that content.**
- `git cat-file -t 20e392e…` → `commit`, exit 0.
- `git rev-parse 20e392e…:tools/kama-probe.sh` → `447e29b397405a3ee9813ca2e44aedf88abe2763`, equal to `manifest.source_blob`.
- `git cat-file blob 20e392e…:tools/kama-probe.sh | sha256sum` → `93ee4302…cd64`, exit 0.

**3. The manifest's own capture command reproduces the snapshot byte-for-byte.**
`git show 20e392ea…:tools/kama-probe.sh > /tmp/…/git-show.sh` → exit 0; its `sha256sum` = `93ee4302…cd64`; `cmp /tmp/…/git-show.sh .ufo/waves/round-16/frozen/kama-probe-before.sh` → exit 0 (identical). Byte count 47443 in all three of blob, snapshot, and `manifest.bytes`.

**4. Independent four-way comparison (not derived from any prior output).** A single python pass hashing `git cat-file blob`, the snapshot file, `manifest["sha256"]`, and `run-before.json["parsed"]["probe_sha256"]` printed `all4_equal True`; `blobbytes 47443 snapbytes 47443 man_bytes 47443`.

**5. run-before.json really does carry it — nested, not top-level.** `run-before.json` top-level keys are `[name, command, cwd, exit, stdout_sha256, parsed, stderr_tail]`; `'probe_sha256' in rb` → `False`. The value lives at `parsed.probe_sha256` = `93ee4302…cd64`, and `parsed.probe` = the absolute frozen path. Its `command` is `python3 …/tests/probe-verdicts/check.py --probe …/frozen/kama-probe-before.sh --json`, `exit: 1`.

**6. The snapshot is committed as-is and the tree is clean.** `git ls-tree HEAD .ufo/waves/round-16/frozen/` → snapshot blob `447e29b…` (same object id as the source commit's), manifest blob `fed2244…`. `git status --porcelain` over those paths and `tools/kama-probe.sh` → empty. So neither file nor source was rewritten after landing.

**7. "Pre-round-16" is real, not a relabel.** `git merge-base --is-ancestor 20e392e… HEAD` → exit 0. `git log --oneline 20e392e..HEAD -- tools/kama-probe.sh` → exactly one commit, `b8e485c round-16: MODEL_LOADING verdict …`. `git cat-file -p 20e392e` → `parent b8bdc56…`, message `round-15 verifier spot-check (integrator, hyaku): non-author admit/reject`. `git rev-parse --disambiguate=20e392e | wc -l` → `1` (unambiguous abbreviation).

**8. The frozen text contains none of the feature, the current one does.**
`grep -c 'MODEL_LOADING'` frozen → `0` (exit 1); `tools/kama-probe.sh` → `7`. `llamacpp-loading` → `0` vs `1`. `Loading model` → `0` vs `3`. HEAD probe sha256 is `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`, 49637 bytes.

**9. The frozen→current delta is exactly C1 and nothing else.** `git diff --no-index --stat` → exit 1 (files differ), `52 insertions(+), 8 deletions(-)`; `old mode 100644 / new mode 100755`. Hunk headers: `@@ -29,0 +30,7 @@` (vocabulary comment + MODEL_LOADING semantics), `@@ -55 +62 @@` (VOCAB), `@@ -110 +117 @@` (help verdict list), `@@ -412,0 +420,29 @@` (`body_is_llamacpp_loading()`), `@@ -466,0 +503,7 @@` (classify branch, `F_CODE = 503` + `-s "$FBODY"` + python exact-triple), `@@ -680/689/699/704 @@` (listeners counters), `@@ -895 +939 @@` (diff_baseline vocabulary tolerance). No unrelated behaviour is touched, which is what makes the red arm a clean control.

# Attribution: the receipt's numbers belong to these bytes

- **Replay.** `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json > /tmp/…/replay-frozen.json` → **exit 1**; stderr tail `tests=72 passes=55 failures=17`; `parsed.probe_sha256` = `93ee4302…cd64` (identical). Failure set equals the `MODEL_LOADING` expectation set exactly (`fail==MODEL_LOADING True n 17`), i.e. no non-loading row fails on the frozen arm.
- **Structural replay identity.** Comparing my fresh run to `run-before.json["parsed"]`, normalising each row's ephemeral port (including the port embedded in `evidence`) and realpath-ing `probe`: `identical modulo ephemeral port: True`. Every `verdict`, `reason`, `served_model`, `evidence`, `passed`, and `probe_exit` reproduces.
- **Receipt is not hand-edited.** `sha256(json.dumps(parsed, indent=2) + "\n")` = `68a15ac3ec5e152e9004193e288276fbf955b30660bb1ab013a1b1488bbe9200` = recorded `stdout_sha256`. The stored `parsed` is exactly the JSON `check.py` printed, so `probe_sha256` belongs to that same document.
- **Declared counts are self-consistent.** `records 72 declared tests 72 passes 55 failures 17`, `expected MODEL_LOADING rows: 17`, `failed rows: 17`, `failed set == MODEL_LOADING set: True`.

# The manifest is a gate, not a note

`.ufo/waves/round-16/measure.py` reads the manifest and verifies the snapshot *before* running anything: `main()` does `manifest = load_manifest()` (`:285`) then `frozen_sha = verify_frozen(manifest)` (`:286`) before the `probes = [("before", FROZEN), ("after", …)]` loop. `verify_frozen` (`:90`) checks `manifest["sha256"]` against the file, `manifest["bytes"]` when integer, and — decisively — `git -C <lane> cat-file blob <source_commit>:<source_path>` and `elif blob.stdout != frozen` (`:126`), exiting `EXIT_FROZEN_MISMATCH = 4` (`:61`) on any problem; unreadable/malformed manifest is `EXIT_MANIFEST = 3` (`:60`). `SKILL.md:531` documents that same contract ("3/4 frozen snapshot manifest or blob mismatch").

Observed controls (imported the module — `main()` is guarded at `:394`, so nothing ran and nothing was written — then called `verify_frozen` directly):

| Case | Result |
|---|---|
| correct manifest | `RETURN 93ee4302718f9786` |
| manifest `sha256` = `0…0` | `SystemExit 4`, "sha256 mismatch: frozen is 93ee4302…, manifest declares 0000…" |
| manifest `bytes` = 47444 | `SystemExit 4`, "byte count mismatch: frozen is 47443, manifest declares 47444" |
| snapshot + `# tamper` | `SystemExit 4`, three problems incl. "frozen snapshot differs from git blob 20e392e…:tools/kama-probe.sh (blob sha256 93ee4302…)" |

I did **not** run `measure.py` itself (lane rule: it rewrites L1 receipts); `sha256sum -c` over `run-before.json`/`run-after.json` before/after my session → `OK`, `OK` (unchanged).

# Limitations and residual weaknesses (do not change the verdict)

1. **`probe_sha256` is nested, not top-level.** The ticket's phrasing "run-before.json's probe_sha256" resolves only via `parsed.probe_sha256`. A consumer that greps the top level finds nothing; nothing in the receipt says the probe identity is one level down. [INFERENCE] This is a usability trap, not an integrity defect.
2. **`check.py` hashes after executing.** `records = [grade(…)]` (`:478`) runs the 72-row matrix, and `"probe_sha256": sha256_file(probe)` (`:486`) reads the file afterwards. Run through `measure.py` the bytes are committed by `verify_frozen` *before* the run, so the window is closed there; run `check.py` directly — which the falsify spec instructs reviewers to do — there is no pre-execution commitment, only a post-hoc read. [INFERENCE] Exploitable only by modifying the snapshot during the ~38 s matrix run; the snapshot is git-tracked and clean, so no such modification is in evidence.
3. **`stdout_sha256` is not replay-stable, by construction.** My replay's stdout hashed `7c7aded3…caaf` ≠ recorded `68a15ac3…9200`, because rows carry ephemeral ports (`"port": 39685`, and the closed-port row's `evidence` embeds `127.0.0.1:50499`). The document is identical modulo those ports. Therefore a `stdout_sha256` mismatch must **not** be read as "a different probe ran"; `probe_sha256` is the only stable identity in the receipt.
4. **`manifest.source_blob` is never checked.** `verify_frozen` does not read that field; it compares against live `git cat-file` output instead (strictly stronger). The declared value is nonetheless correct (`447e29b…`), verified independently in link 2.
5. **mtime proves nothing here.** All wave artifacts and the commit share mtime `2026-10-20 10:50:49.145…` (checkout instant), so no ordering evidence was drawn from timestamps — the chain rests on content addressing only.
6. **Mode differs, harmlessly.** Snapshot is `100644`, HEAD's probe is `100755`; `check.py` invokes `["bash", str(probe), …]` (`:274`), so the executed bytes are the file contents regardless of the bit. Anything that exec'd the snapshot directly would fail.
7. **Forgery cost, for the record.** To fake this chain one would have to rewrite a pre-existing round-15 commit's tree (`20e392e`, parent `b8bdc56`) *and* keep `b8e485c` the only later commit touching the path — history rewrite, not file edits. [INFERENCE] Out of reach for a single wave's file writes.
8. **One stale historical claim, outside lane docs.** `build/advice/ScribeSkillSection.md:18` says "Frozen probe matches the current probe … both give `93ee4302…`" — true when written ("The repair has not landed"), false at HEAD now that the probe is `6edd3c4c…`. It lives only in build-wave advice; no lane doc (`SKILL.md`, `corpus/`) repeats the equality claim (`grep` for it → no hits), so nothing shipped is wrong.

# Installs

None. No package was installed or upgraded; no tool was needed beyond `git`, `python3`, `sha256sum`, `cmp`, `grep`. No `llama-server` was started (this item did not permit it), so nothing needed tearing down; no port was bound or probed, and `8080`/`34113` were never contacted. Scratch `/tmp/kama-r16-RevengerFrozenProvenance/` used for the replay and tamper fixtures, then removed.
