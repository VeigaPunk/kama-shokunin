ATTACK C1 shortcut-rows: partial — the frozen counter can be met 12/12 from the base tree with no server error knowledge, but none of the 17 landed rows is of a shortcut type.

# CriticShortcutRows, round 26 wave 2 (lane kama, tip f4066979)

Scope: whether the frozen C1 counter could have been met without the claimed work
(warning-only startup lines, decoded-echo bodies, argument-file echoes, id/label-keyed
rows), and whether any of the 17 landed rows is of a shortcut type.

Everything below was run from a scratch clone and scratch extracts under
`/fast/scratch/hyaku/kama-r26w2/CriticShortcutRows/`. No lane production file was
edited. No tool was installed or updated. `~/.local/bin/llama-server --help` and
`--version` were run (informational, exit 0, no server, no port). All servers were
started by the frozen counter itself, one child at a time, on its own block
127.0.0.1:47560-47579; `ss -ltn` showed the block free before each run; after both
runs `pgrep -af llama-server | grep -E ':475[67][0-9]\b'` printed nothing and
`ss -ltn | grep -E ':475[67][0-9]\b'` printed nothing. Three peer servers on
47719/47734/47740 were already running; I did not touch them.

## 1. Shortcut control receipt (the requested counterexample)

Tree: `git archive 1560e4d83f42b04f40336357de6f9637eafa0f4b` extracted to
`scratch/.../tree`, plus the pinned snapshot `.ufo/waves/round-26/sources/llama.cpp-704366d/`
(13 files, sha256 equal to the counter's `SOURCE_SHA256`, and equal to a fresh
fetch at 704366d76 — see §4), the frozen counter copied in
(`sha256 6501737c749926be9d6b37761175d76f89876976c46bd5951fc1a3520c796588`, equal
to `preregistration.json` `counter_sha256`), a new SKILL.md section, 12 SOURCES rows
S901-S912, and a 12-row registry `registry/error-signatures-r26.json`. The tree is
built from BASE, so it contains none of the round's work.

Exact command (under the host-wide lock, as the contract requires):

```
cd /fast/scratch/hyaku/kama-r26w2/CriticShortcutRows/tree
flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 \
  .ufo/waves/round-26/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r26w2/CriticShortcutRows/repo \
  --out  /fast/scratch/hyaku/kama-r26w2/CriticShortcutRows/receipts/shortcut.json
```

Output (exit 0, wall 3.44 s):

```
registered 12 counted 12 target 12 met True not-counted []
```

Receipt: `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json`
(sha256 `6020a2c39cf698860f64216754925ed623c7225c47871a1644e0c8e6d3d7ac19`).
Every row has all twelve checks true (`id_unique, a_skill_row, b_long,
b_new_at_base, c_source_row, d_source_pinned, d_in_source, e_error_shown,
e_signature_seen, e_not_echoed, f_absent_from_baseline, g_distinct`), `status: 400`,
and a distinct `channel_sha256`.

`--repo` pointed at the scratch clone, not at the lane: the clone resolves both
BASE `1560e4d8…` and tip `f4066979…` (verified with `git rev-parse --verify`), and a
clone cannot differ in object content. Base reads are therefore identical to the
lane's; the tree scored is the extract, not the lane.

### The mechanism (one server-side echo, twelve arbitrary literals)

`server-common.cpp:1375` (pinned file, upstream-verified) is

```cpp
throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);
```

So `POST /v1/chat/completions` with `response_format.type` set to any non-empty
string other than `text`/`json_object`/`json_schema` returns 400 and copies the
client string into `error.message`. The counter compares the signature with the
raw registry text only (`count-c1.py:372-374` builds `req_bytes`; `:384` is
`e_not_echoed = sig not in req_bytes`), and the server decodes JSON escapes before
echoing. Writing the first character of the injected value as `\u00XX` hides it
from that comparison:

```
{"messages":[{"role":"user","content":"Hi"}],"response_format":{"type":"\u005fNSGetExecutablePath failed after buffer resize"}}
```

gives

```
{"error":{"code":400,"message":"response_format type must be one of \"text\" or \"json_object\", but got: _NSGetExecutablePath failed after buffer resize","type":"invalid_request_error"}}
```

`e_error_shown` is satisfied by status >= 400 (`count-c1.py:296`), regardless of
what the error is about. Each row needs only a distinct trigger JSON for
`g_distinct` (`:392-395` compares `trig_key`, which changes with the injected
string), and all twelve runs use the same server configuration and endpoint —
one fault site, twelve bodies.

### Why the twelve signatures encode no error knowledge

They are pinned-source literals chosen so that this build cannot emit them as a
response to any trigger the counter can run; several are compile-time or
other-platform strings:

| row | literal | pinned file | why it is not an error here |
|---|---|---|---|
| X26-01 | `_NSGetExecutablePath failed after buffer resize` | server-common.cpp | macOS branch |
| X26-02 | `GetModuleFileNameW failed or path too long` | server-common.cpp | Windows branch |
| X26-03 | `RPC not supported in this build` | arg.cpp | build-option validation |
| X26-04 | `T must be trivially copyable` | server-common.cpp | static_assert text, never printed |
| X26-05 | `yield_to_queue() cannot be nested` | server-queue.cpp | internal guard |
| X26-06 | `update() must be called before to_json()` | server-task.cpp | internal programmer error |
| X26-07 | `Invalid task_response_type` | server-task.cpp | internal enum guard |
| X26-08 | `unsupported batch.has_embd + spec case` | server-context.cpp | internal branch |
| X26-09 | `Error: gzip is not supported by this browser` | server-http.cpp | browser-side JS in the embedded page |
| X26-10 | `CLIP cannot be used as main model, use it with --mmproj instead` | llama.cpp | needs a CLIP model; counter models are fixture/missing/junk |
| X26-11 | `Cannot restore media tokens without an mmproj` | server-common.cpp | needs a media-bearing token state |
| X26-12 | `sampling tensor must be contiguous for async copy` | llama-context.cpp | backend path the fixture does not take |

So the answer to "could the frozen counter have been met without the claimed work"
is yes: 12 counted rows, target met, from the base tree, with one known echo
behaviour and zero knowledge of llama-server error conditions. The preregistration's
own required shortcut control (`controls_required` item 5, "shortcut keyed on ids
or labels (… request-echo …)") never ran — seat `KamaR26CtlShortcut` is recorded as
"held" in `preregistration.json` `control_wave.seats`. This receipt supplies the
missing observation after data; by the round's own rule (lesson §Mistakes row 3) the
frozen predicate is not amended after data, so this is an instrument defect for a
future round, not a rescale of C1.

### Independent reproduction of the landed claim

The same frozen counter, in a fresh `git archive f4066979…` extract, with the lane's
own registry and SKILL.md (`receipts/landed-tip.json`,
`.../out/CriticShortcutRows/landed-tip.receipt.json`, sha256
`362f96c136a7527955fc11597a954b10c727aa1abac1ba49ba2543d234b745b4`):

```
registered 17 counted 17 target 12 met True not-counted []
```

exit 0, 4.62 s. The receipt transfers to the landed tip: `git diff --stat 7e5ff9b5
f4066979` (the count tree named in `final/c1-tip.out` versus the landed tip) touches
only `LOG.md` and `.ufo/waves/round-26/{final,w1-build}` files — not SKILL.md, not
`corpus/SOURCES.md`, not `registry/error-signatures-r26.json`, not the counter, not
the source snapshot.

## 2. Per-row shortcut verdict: all 17 rows clean

Method: for each registry row I tested the counter's own inputs *and* the stronger
forms wave 1 did not implement: the request body parsed with `json.loads` and every
decoded key/string value, `urllib.parse.unquote(path)`, and header values (the
reviewer's F2 fix proposal); any ≥8-byte decoded request string inside the
signature; file-argument scope (F3); source-line log level for the startup rows
(F1); pairwise signature containment (the A0 "split message" rule); and base-tree
documentation presence (`.ufo/waves` evidence, not just SKILL.md and corpus/).

| row | channel | F1 warning | F2 echo (decoded) | F3 file contents | label/id | split msg | in *.md at BASE | verdict |
|---|---|---|---|---|---|---|---|---|
| E26-01 | http 501 | n/a | no | no | no (message) | no | no | genuine |
| E26-02 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-03 | http 400 | n/a | no | no (see note) | no | no | no | genuine |
| E26-04 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-05 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-06 | http 400 | n/a | no | no | no | no | no | genuine |
| E26-07 | http 400 | n/a | no | no | no | no | no | genuine |
| E26-08 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-09 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-10 | http 500 | n/a | no | no | no | no | no | genuine |
| E26-11 | http 400 | n/a | no | no | no | no | no | genuine |
| E26-12 | http 501 | n/a | no | no | no | no | no | genuine |
| E26-13 | http 500 | n/a | no | no | no | no | no | genuine |
| E26-14 | http 400 | n/a | no | no | no | no | no | genuine |
| E26-15 | startup exit 1 | no (E-level cause) | n/a | no | no | no | no | genuine |
| E26-16 | startup exit 1 | no (E-level cause) | n/a | no | no | no | no | genuine |
| E26-17 | startup SIGABRT | no (assert) | n/a | no | no | no | no | genuine |

Per-type evidence:

- F2 (decoded echo): for every http row, the signature occurs in neither the raw
  request fields nor any decoded JSON string of the request, and no decoded request
  string of 8+ bytes occurs in the signature. I re-derived each signature from the
  server's own code path: all fifteen http signatures sit on a `res->error(...)`,
  `send_error(...)` or `throw` line in the pinned file (`server-context.cpp` lines
  5366, 5408, 3084, 5453, 6132, 6137, 6151, 5803, 5476, 3657 (`send_error` at
  3655-3660), 5998, 5655; `server-common.cpp` 1272, 1114; verified upstream — §4).
  Every cited code range in the "meaning (code)" cells contains its signature line
  (17/17 checked). The tip receipt's channel excerpts are server
  error envelopes, not echoes: e.g. E26-03
  `{"error":{"code":400,"message":"Unable to restore slot: No available space in KV cache or invalid slot save file",...}}`.
- F3 (argument-file contents): no landed row passes a file whose contents can reach
  the channel. E26-03's only path-like argument is `--slot-save-path /tmp` (a
  directory) and its request names `kama-r26-absent-slot.bin`, which does not exist;
  there is no `--chat-template-file`, `-f`, `--grammar-file`, `-jf`, `--lora`,
  `--mmproj` or `--models-preset` anywhere in the 17 rows. E26-15's model path does
  not exist and E26-16's junk file is the counter's own text fixture
  (`count-c1.py` `model_path("junk")`); the E26-16 signature stops at
  `invalid magic characters: '` and the file's bytes appear only after it as the
  four `%c` fills. Note the counter's echo check also omits `base_argv` (the `-m`
  path), so a model-path echo is not covered — no ≥20-byte pinned literal is a
  substring of those paths, so it is a residual hole, not a landed one.
- F1 (warning on an unrelated failure): the three startup rows are not warnings.
  Wave-1 logs, observed again here by `grep`:
  - `.ufo/waves/round-26/w1-build/out/ExecMissingModel/raw/run1.log:5` —
    `0.00.005.000 E gguf_init_from_file: failed to open GGUF file '/nonexistent/kama-r26/missing.gguf' (No such file or directory)`
  - `.ufo/waves/round-26/w1-build/out/ExecJunkModel/junk-run1.log:5` —
    `0.00.006.442 E gguf_init_from_reader: invalid magic characters: 'this', expected 'GGUF'`
  - `.ufo/waves/round-26/w1-build/out/ExecBadArgs/raw/cand12-rep1.log:5` —
    `/home/runner/work/llama.cpp/llama.cpp/src/llama-context.cpp:2624: GGML_ASSERT(n_outputs >= 1) failed`
  Each signature is the `E`-level line (or the assert line) of the failure that
  produced the non-zero exit, not a warning printed beside a different fault. The
  counter's weak form (`error_shown = rc != 0`, `count-c1.py:281-285`) is not what
  carries these rows: the row's own log evidence does.
- Label/id keyed: every signature is a ≥20-byte message, none is an error-type
  label (`invalid_request_error`, `not_supported_error`, …).
- Split message (A0 rule): no signature is a substring of another among the 17 and
  no observed channel text contains another row's signature (each body/log carries
  only its own message), so `g_distinct` is order-independent for this registry;
  the reviewer's F9 order artefact does not apply here.
- Already-held signature (the "rows reusing signatures the lane already holds"
  path): `git grep -F -l -e <sig> 1560e4d8 -- '*.md'` returned no file for all 17.
  The only base-tree hits are earlier copies of the pinned llama.cpp sources
  (`.ufo/waves/round-16|17|21/sources/...`) and one source-excerpt file for
  E26-16 (`.ufo/waves/round-20/build/out/SrcGgufPyReader/source-excerpts.txt`) —
  the same upstream line, not lane-held error knowledge. Clause (b) is correctly
  scoped to SKILL.md and corpus/ (`count-c1.py:114-119`).

Claimed versus observed statuses match for all 17 (SKILL cells `→ 501/400/500/
exit 1` against `final/c1-tip-receipt.json` observed values; E26-17 is claimed as
exit status 134 / SIGABRT and is recorded as `-6` by Python, the same signal).

## 3. Defects (none in the 17 rows; three in the instrument, one in the section text)

1. HIGH, instrument: the frozen counter is not a sound falsifier — the receipt in §1
   is a 12/12 pass from base with no error knowledge. Smallest safe correction for
   a future counter (round 27; the frozen rule must not change now):
   (a) decode the request before `e_not_echoed` (parse a string body with
   `json.loads`, add every decoded key/value, `unquote` the path, include header
   values) and refuse a row if any decoded request string of ≥8 bytes occurs in the
   signature or in the observed message; (b) require the observed body's
   `error.message` to contain the signature; (c) for startup rows require the
   signature line to be error-level/assert and require a healthy control run of the
   same argv (fixture model, fault argument removed) that does not print it;
   (d) require a distinct *fault site*, not merely a distinct trigger JSON, so one
   echo endpoint cannot carry many rows.
2. HIGH, instrument integrity (reviewer F7, still unmitigated and not listed in
   lesson §Mistakes): the pin covers the 17,864-byte launcher only.
   `~/.local/bin/llama-server` is a symlink to
   `~/.local/opt/llama-b11755/llama-server`; `readelf -d` shows
   `NEEDED libllama-server-impl.so` with `RUNPATH [$ORIGIN]`, and that library
   (7.3 MB, sha256 starts `e404b91a…`) plus `libllama.so.0`, `libllama-common.so.0`
   and the ggml backends are not hashed; `LD_*` is inherited. Every live row's
   evidence rests on these files. Correction: pin every regular file the launcher
   loads under `~/.local/opt/llama-b11755/` and run children with `LD_*` cleared.
3. MEDIUM, instrument capacity / premature saturation: `used.add(p)` is never
   undone (`count-c1.py:148-153`), so at most 19 rows can be evaluated (F4). The
   round filled 17 of those 19 slots, and the lesson records ~17 further
   live-confirmed signatures held back solely by the limit. Separately, 5 of the 17
   landed rows (E26-01, -02, -04, -05, -08) are one template,
   `This server does not support <thing>. Start it with <flag>`, so the section's
   independent decision content is below its row count. This is a tradeoff for the
   depth axis, not a defect of the rows, but a depth round that cannot add rows
   without the instrument breaking is at its ceiling. Correction: free the port
   after confirmed teardown (or re-probe) before the next depth round.
4. LOW, section text: `SKILL.md` "Round-26 live error signatures" intro says each
   row is an error the server "emits on the lane fixture (`stories260K.gguf`, …)".
   E26-15 (missing model path) and E26-16 (junk file) do not run the fixture model.
   Correction: replace "on the lane fixture (`stories260K.gguf`, loopback, one child
   at a time)" with "on the lane fixture's server — the pinned fixture model for 15
   rows, a missing path and a junk file for the two model-load rows — loopback, one
   child at a time". No data changes.

## 4. Provenance, identity and novelty checks (all pass)

- Fresh fetch, 2026-10-23, `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…`:
  all 13 pinned files match `SOURCE_SHA256` and the lane snapshot byte for byte
  (arg.cpp `bf4c58c1…`, common.cpp `d10ea1ff…`, gguf.cpp `7505d6a4…`,
  llama-context.cpp `2a25e556…`, llama-model-loader.cpp `7975d834…`, llama.cpp
  `8058a140…`, server-common.cpp `b4f4aae7…`, server-context.cpp `dd1de0f2…`,
  server-http.cpp `24ede172…`, server-models.cpp `9c5a6f2c…`, server-queue.cpp
  `168385b7…`, server-task.cpp `4c3f413b…`, server.cpp `2143962217…`).
- All 17 cited lines contain the cited literal (inline Python line check: 17/17 OK,
  e.g. `server-context.cpp:5366`, `server-common.cpp:1375`, `gguf.cpp:1021`,
  `llama-context.cpp:2624`).
- Build identity: `~/.local/bin/llama-server --version` →
  `version: 0.7.0-dev (build 11755, commit 704366d76)`; binary sha256
  `b6a31a8e…cd804`, model sha256 `270cba1b…256d`, both equal to the counter pins.
- Old rows: 113 SOURCES rows at BASE, 113 still present at the tip, 0 changed;
  new rows at the tip are S114-S135 exactly (S114-S130 used by the 17 rows,
  S131-S135 the KQ31 supersession rows).
- `found_by` provenance: every seat named in the registry
  (`ExecSlotsOff`, `ExecSlotActionNoPath`, `ExecPropsOff`, `ExecEmbeddingsOff`,
  `ExecEmbeddingsInput`, `ExecRerankOff`, `ExecInfill`, `ExecPromptTooLong`,
  `ExecLoraAudio`, `ExecRequestParams`, `ExecMissingModel`, `ExecJunkModel`,
  `ExecBadArgs`) exists under `.ufo/waves/round-26/w1-build/out/` and its files
  contain the row's signature. No false provenance found.
- Novelty: no signature appears in SKILL.md or corpus/ at BASE (clause b), and none
  appears in any `.md` anywhere in the BASE tree.

## 5. Axes and harm

- depth (the claimed axis): the 17 rows are new to SKILL.md/corpus, source-pinned,
  live, and independently reproduced. Depth genuinely increases by 17 rows [INFERENCE:
  about 12 independent decision facts after the five-template discount]. But the "met
  True" signal is not what certifies it: the instrument also passes a 0-knowledge
  control (§1), so the depth evidence is the rows' own logs and source lines, which
  I re-verified.
- calibration: the instrument is miscalibrated — a control reaching the same
  `counted >= 12` means the predicate does not discriminate work from echo. This is
  the axis the round must *not* claim to have improved.
- adjacency: unchanged (the section cites kagi/tsukuroi/kengaku scope instead of
  absorbing it; `SKILL.md` "Cited, not absorbed" paragraph).
- No harm to any landed row; the harm is to future depth rounds that would rely on
  this counter, and (small) to a reader who takes the intro's "on the lane fixture"
  sentence literally.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/CriticShortcutRows.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json`
  (counted 12/12, sha256 `6020a2c3…d7ac19`)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/landed-tip.receipt.json`
  (landed 17/17, sha256 `362f96c1…b745b4`)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.registry.json`
  (sha256 `1b78c8aa…91b91`)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/gen_shortcut.py`
  (sha256 `1a236f80…e2f178`)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.SKILL.section.md`
  (sha256 `e503c2af…5d5319`)
- `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.SOURCES.rows.md`
  (sha256 `c0aebf4d…49c4`)

Report: .ufo/waves/round-26/w2-falsify/advice/CriticShortcutRows.md
