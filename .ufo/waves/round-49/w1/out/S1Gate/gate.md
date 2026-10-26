# Round 49 gate — lane kama (seat S1Gate)

**Verdict: ACCEPT both claims on the counters' own runs at the build tip — C1 `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`, C2 `fixture=1 lane=1 scenarios=8/8 met=True`, both counters fail at the base — while REJECTING four substitute witnesses that a loopback stub or a stale lane satisfies without the claimed work.**

Lane `kama`. Freeze commit `36d5ed2681111b68c180f8ab1646d8dc9beaedee` (preregistration + frozen counters + controls, 2026-10-26T23:17:45Z), base / round-48 closure `438127bc01ff3b99f98468549d58046f932490ef`, build `74558c71c38ceaeace15fd4cf8aa9d84977584b1` (single commit on the freeze). Every number below comes from a command I ran against my own `git clone --shared` of the lane at those commits; receipts are copied into this directory. The lane tree was read-only; no lane file was edited, no lane git/jj state touched.

Frozen counter files at the tip hash exactly to the preregistration's `counter_sha256`:

```
$ git -C $S/lane show 74558c71:tools/round49-replay-witness-audit.py | sha256sum
86b4a40dd027ad7dd62c71c9694b354d52e88ffdfc04aa83a1bb648799f0d6c1   (preregistration: same)
$ git -C $S/lane show 74558c71:tools/round49-append-audit-v4-check.py | sha256sum
26c465a9830b6894160190a8ac777bdb006b79ec421586adb6527f12ab066945   (preregistration: same)
$ git -C $S/lane log --oneline 438127bc..74558c71
74558c71 round-49: build - replay execution witness (--witness-dir), bounded archive-member verification, append-only-audit v4 definitions, SOURCES S494-S495
36d5ed26 round-49: freeze - C1 replay-witness and C2 append-audit-v4 counters, preregistration, controls, start census, C1 source captures
```

## Decisions

| # | axis | proposal before the gate | verdict |
|---|---|---|---|
| D1 | operability | `/health` 200 and/or `/props` `model_path` is an execution witness | **REJECT** |
| D2 | operability | `/proc/<pid>/cmdline` naming `-m <model>` is model proof | **REJECT** |
| D3 | operability | a `piece` comparison that is self-consistent between `/tokenize` and `/detokenize` is tokenizer proof | **REJECT** |
| D4 | operability | the conjunction `exe ∧ listen-owned ∧ -m-hash ∧ nonce-pieces-vs-counter-GGUF ∧ gone-after-release` is the execution witness | **ACCEPT** (3/3 at tip) |
| D5 | operability | bounded archive-member verification (`cap`) is record-time evidence | **ACCEPT** (tip 0.1 s refusal; base 30 s timeout) |
| D6 | operability | the `/tokenize` source row is registry presence, nothing more | **ACCEPT as presence only** |
| D7 | calibration | the lane leg's `tool exit 0` / `bad_declarations 0` is calibration evidence | **REJECT** (base holds both while 4/8 fixtures fail) |
| D8 | calibration | v4 origin rule closes the K1Regions laundry hatch | **ACCEPT** (launder graded 25; 7 lane lines regraded) |
| D9 | calibration | whole-word token + 3-word negation window + no wildcard self-declaration bind rows correctly | **ACCEPT with the punctuation limit below** |
| D10 | calibration | `ungraded ≤ natively-exempt` per event is a discriminating lane bound | **ACCEPT** (65 ≤ 65 at tip; 72 > 65 at base) |

### D1 — REJECT `/health` 200 or `/props` `model_path` as an execution witness

**Claim.** A gate could accept a replay as having executed the recorded server because the listener answers `GET /health` with 200 `{"status":"ok"}`, and/or because `GET /props` returns the recorded `model_path`.

**Evidence.**

```
$ S=/fast/scratch/hyaku/kama-r49/S1Gate; LANE=$S/lane MODEL=$S/model.gguf SCRATCH=$S \
  OUT=<out>/S1Gate python3 <out>/S1Gate/gate_rejects.py      # probe A
A: GET /health status=200 body={"status": "ok"}
A: GET /props status=200 model_path=/fast/scratch/hyaku/kama-r49/S1Gate/model.gguf sha=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d frozen_model=1
A: pid 504422 port 47097
A: exe sha256=375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b frozen_server=0 frozen=35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
A: listen inodes=['620996514'] owned_by_pid=1
A: cmdline -m /fast/scratch/hyaku/kama-r49/S1Gate/model.gguf sha=270cba1b… frozen_model=1
A: counter observe() nonce='kama witness f12fc0ce9f27e9ca' problems=["exe sha256 375532f8… is not the frozen server"]
```

Probe A is a small `http.server` stub (`gate_rejects.py`, child `CHILD`, ~45 lines), not llama-server. It answers `/health` 200, returns a `model_path` that is a *real file hashing to the frozen model*, owns the listening socket, names `-m <frozen model>` in its own argv, and round-trips the counter's nonce through `/tokenize`/`/detokenize` with the model's own vocabulary. The frozen counter's `observe()` (`tools/round49-replay-witness-audit.py:258`) reports **exactly one** problem: the exe digest. Everything these two proposed witnesses would show is served by a stub.

The frozen fake-witness control independently shows the same shape at counter level (`.ufo/waves/round-49/controls/junk-c1-fake-witness.c1.out`): a replay that never runs llama-server fails only `witness w1..w3: exe sha256 375532f8… is not the frozen server`.

**Verdict. REJECT** — individually or together. `/health` reports the server's own view of itself; `/props` reports a string the server chooses. Neither is outside the process's control.

**Flip condition.** Flip only if those fields are read through a channel an unprivileged process cannot author (e.g. the process's own open file table showing the model fd with the frozen inode and size *and* the exe digest matching), and a stub is shown unable to present that. Not met: my stub named a real file with the frozen digest.

### D2 — REJECT `/proc/<pid>/cmdline` alone as model proof

**Claim.** `-m <path>` in the listener's argv, hashing to the frozen model digest, proves the model was loaded.

**Evidence.**

```
$ … python3 <out>/S1Gate/gate_rejects.py      # probe B
B: pid 504723 argv=["/usr/bin/python3", "-c", "import time; time.sleep(120)", "-m", "/fast/scratch/hyaku/kama-r49/S1Gate/model.gguf", ""]
B: cmdline -m /fast/scratch/hyaku/kama-r49/S1Gate/model.gguf sha=270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d frozen_model=1 sockets=0
B: exe sha256=375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b frozen_server=0
```

A plain `python3 -c "time.sleep(120)" -m <frozen model>` names the frozen model in argv (hash matches) and owns **no socket at all**. The frozen control does the same thing inside a replay (`build_controls.py` FAKE_REPLAY launches `[sys.executable, stub, "-m", model, …]`). argv is chosen by the process; there is no binding between `-m` and what was loaded. The same leg in the counter (`tools/round49-replay-witness-audit.py:267-274`) is worth keeping only as a consistency check *next to* the exe digest, which is what the frozen counter does.

**Verdict. REJECT.**

**Flip condition.** Flip only if argv is attested outside the process (kernel exec audit, signed audit log) or the model file's open fd is witnessed by the counter (`/proc/<pid>/fd` → same inode/size as the frozen model). A python process can open that file too, so even the fd check needs the exe digest beside it.

### D3 — REJECT a `piece` comparison without the model's own vocabulary

**Claim.** If `/tokenize` returns `{"id", "piece"}` and `/detokenize` returns the nonce from those ids, the server is tokenizing with the recorded model.

**Evidence.**

```
$ … python3 <out>/S1Gate/gate_rejects.py      # probe C
C: nonce='kama witness 84acab0e495322ff' tokenize=[{"id": 0, "piece": "kam"}, {"id": 1, "piece": "a w"}, {"id": 2, "piece": "itn"}, … {"id": 9, "piece": "ff"}]
C: detokenize 'kama witness 84acab0e495322ff' equals_nonce=1 (a detokenize-only check passes)
C: pieces disagreeing with the model vocabulary=10/10 example=[{"id": 0, "piece": "kam"}] vocab[0]='<unk>'
C: counter observe() problems=["exe sha256 375532f8… is not the frozen server", "tokenize pieces disagree with the model vocabulary: [{'id': 0, 'piece': 'kam'}, …]"]
```

Probe C invents a 3-character vocabulary; tokenize/detokenize are perfectly self-consistent (`equals_nonce=1`) and every piece is wrong against the GGUF. A check that only compares the server's two answers to each other passes. The frozen counter only accepts a piece when `vocab[id].replace("\u2581", " ") == piece`, with `vocab` decoded by the counter itself from the model it downloaded from the frozen URL and hashed (`:275-283`, `gguf_tokens()` at `:144`). That leg is the whole difference between D3 and D4.

**Verdict. REJECT** — self-consistency is not tokenizer evidence; the comparison must be anchored to a vocabulary the counter derives independently.

**Flip condition.** Flip if the comparison is anchored in data the server cannot obtain except from the model and the counter derives independently (that is exactly the accepted GGUF-decode leg, `:283`), or if a fake-vocabulary stub is shown unable to round-trip the nonce (it is not).

### D4 — ACCEPT the conjunction as the execution witness

**Claim.** An outside observer sees the frozen llama-server binary executing as the listener of the announced port, with the frozen model, answers a fresh nonce from the model's vocabulary, and sees it gone after release.

**Evidence.**

```
$ python3 tools/round49-replay-witness-audit.py --repo $S/lane --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch $S/sc1r --out $S/c1.out
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
witness=1 cap=1 newrow=1 witnessed=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: witness w1: pid 1768075 port 44443 exe+listen+model ok, nonce 'kama witness 3d6cef08fd026e47' round-tripped
detail: witness w2: pid 1778812 port 35935 exe+listen+model ok, nonce 'kama witness 9c8e2e205293c2a9' round-tripped
detail: witness w3: pid 1792942 port 42749 exe+listen+model ok, nonce 'kama witness 9f16f10fec01e921' round-tripped
exit=0
```

The witness legs are each necessary and jointly not satisfiable by a stub: probes A/B/C cover every leg except the exe digest, and each passes it with a stub. Receipt: `c1.tip-74558c71.out`.

**Verdict. ACCEPT** for operability 8→8, conditional on the counter running at the measured commit (as here) and on the preregistered limits below.

**Flip condition.** Flip to REJECT if any single leg is satisfiable without executing the frozen binary while the other legs hold (probes A/B/C show the listen-owned, `-m`-hash, nonce-piece and gone-after-release legs are all satisfiable without executing the frozen binary; the exe digest is the load-bearing leg), or if `/proc/<pid>/exe` can hash to `35ac50fb…` without that binary executing. Also flip if the counter's vocabulary download stops being hashed against `270cba1b…` (then a stub could learn the vocabulary from a substituted model); at tip the vocabulary model is downloaded and hashed at `:442` before `gguf_tokens()` at `:445`.

### D5 — ACCEPT bounded archive-member verification (`cap`)

**Claim.** Record-time verification refuses a sparse or size-mismatched archive member before hashing it, and still executes the member when it is regular and matching.

**Evidence.**

```
$ … --tip 74558c71 … (same run as D4)
detail: cap sparse-1e15: exit 2 setup_error 'provenance-member-sparse' executed=False seconds=0.1 ok
detail: cap member-is-server-control: exit 2 setup_error 'server-exited-early-rc3' executed=True seconds=0.1 ok

$ … --tip 438127bc01ff3b99f98468549d58046f932490ef …        # base, my own run
detail: cap sparse-1e15: exit None setup_error None executed=False seconds=30.0 FAIL
```

At tip the 10^15-byte sparse archive is refused in 0.1 s (`provenance-member-sparse`) and the stub is not executed; the positive control is executed. At base the same input runs the counter's 30 s timeout with no refusal. Implementation at `tools/kama-llamacpp-live.py:212-265` (`verify_archive_member`; tokens at `:232` not-regular, `:234` too-large, `:253` too-many-members, `:261` member-sparse, `:263` member-size-mismatch; cap `ARCHIVE_MAX_BYTES = 1 << 30` at `:208`). Receipt: `c1.base-438127bc.out`.

**Verdict. ACCEPT** for the sparse and size-mismatch legs exercised. **Un-exercised surface (gate limit):** `provenance-archive-not-regular`, `provenance-archive-too-large` and `provenance-archive-too-many-members` exist in the tool and in its selftest (`:1391-1393`) but the frozen counter's `cap` leg never exercises them; the gate may not claim those from this counter.

**Flip condition.** Flip if a sparse or size-mismatched archive passes verification at tip, or if the 1 GiB / 4096-entry / regular-file bounds are shown bypassable (then the tool's own selftest tokens, not this counter, are the evidence and the claim narrows).

### D6 — ACCEPT the `/tokenize` source row as registry presence only

**Claim.** The tokenize surface is sourced.

**Evidence.**

```
$ git -C $S/lane show 74558c71:corpus/SOURCES.md | grep -n '^| S49[45] '
247:| S494 | llama.cpp server README at b11909 — https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md | … `/tokenize` (with `with_pieces`) and `/detokenize` … |
248:| S495 | Linux proc_pid_exe(5) — https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | … hashing `/proc/<pid>/exe` identifies the binary a listener is really running, whatever path or wrapper started it | …

counter: detail: newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']
```

**Verdict. ACCEPT as presence.** The counter checks row presence plus the frozen README commit and the endpoint string (`newrow_leg`, `:394`); it does not read the captured README (`.ufo/waves/round-49/c1/server-README-caa8191d.md`) or verify the quoted text. A gate must not read `newrow=1` as evidence that the documented request/response shape was followed — D4's live nonce is that evidence.

**Flip condition.** Flip if the row's URL drifts off the frozen commit or loses `/tokenize` (the counter then reports 0), or if the gate starts treating a registry row as execution evidence.

### D7 — REJECT `tool exit 0` / `bad_declarations 0` on the lane as calibration evidence

**Claim.** Because the lane's own audit exits 0 with no unbound declaration, the audit's rule is calibrated.

**Evidence.**

```
$ python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 438127bc01ff3b99f98468549d58046f932490ef --scratch $S/sc2b --out $S/c2.base.out
tip=438127bc01ff3b99f98468549d58046f932490ef
fixture=0 lane=0 scenarios=4/8 met=False
detail: scenario launder: FAIL exit 0 (want 1)
detail: scenario substring: FAIL exit 0 (want 1)
detail: scenario negated: FAIL exit 0 (want 1)
detail: scenario wildcard-self: FAIL exit 0 (want 1)
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 72 > natively exempt 65
exit=1
```

At base the lane leg's two "clean" numbers hold while four constructed fixtures fail and the lane already carries an event whose ungraded count exceeds the exempt count. A clean lane tells you the lane did not happen to trip the rule; it does not tell you the rule grades the defect. My run is byte-identical to the frozen control `.ufo/waves/round-49/controls/base.c2.out` (diff: only the control builder's appended `exit=1` line).

**Verdict. REJECT.**

**Flip condition.** Flip only if the lane leg is extended to replay the fixture conditions on the lane's own history (i.e. `lane=1` implies `fixture=1` by construction). Today the two legs are independent and must be read together.

### D8 — ACCEPT the v4 origin rule for the K1Regions hatch

**Claim.** A deleted line in an exempt `## ` section is ungraded only if its text was born in an exempt section; dated text laundered under an exempt heading and dropped is graded.

**Evidence.**

```
$ python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S/sc2r --out $S/c2.out
tip=74558c71c38ceaeace15fd4cf8aa9d84977584b1
fixture=1 lane=1 scenarios=8/8 met=True
detail: scenario launder: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'ungraded': 0, 'status': 'unrestored'}
detail: scenario native-head: ok exit 0 (want 0) event {'deleted': 25, 'graded': 0, 'ungraded': 25, 'status': 'ungraded'}
detail: scenario dated-loss: ok exit 1 (want 1) event {'deleted': 25, 'graded': 25, 'status': 'unrestored'}
detail: lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 82
detail: lane: event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23
detail: lane: event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65
exit=0
```

Against the base run (89 ungraded lines, event 72 > 65), the build regrades 7 lines of the `0718b6ab` SCORECARD.md event (72 → 65, total 89 → 82) and keeps the native head carve-out (25 ungraded, exit 0). Implementation: `tools/append-only-audit.py:423-432` (`origins()`), applied at `:474` (`if s in eligible and org.get(text, frozenset()) & titles`). Receipts: `c2.tip-74558c71.out`, `c2.base-438127bc.out`.

**Verdict. ACCEPT**, within the preregistered limit: origin is the text's first appearance in the file, so a line born in the head, later carried in a dated section and deleted from the head again stays ungraded; identical text born in both places counts as exempt-born.

**Flip condition.** Flip if a line whose origin is not an exempt section is reported ungraded at the measured commit on the lane's real history, or if the launder fixture stops being graded (it is graded at tip, ungraded at base).

### D9 — ACCEPT the v4 binding rules, with one punctuation limit

**Claim.** The row token must match as a whole word, a negation within three words before `append-only` unbinds, and a wildcard row is not bound by a covered file's self-declaration.

**Evidence.**

```
$ … --tip 74558c71 … (same run as D8)
detail: scenario substring: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario word-token: ok exit 0 (want 0) bad_declarations 0 want 0
detail: scenario negated: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-self: ok exit 1 (want 1) bad_declarations 1 want 1
detail: scenario wildcard-named: ok exit 0 (want 0) bad_declarations 0 want 0

$ python3 - <<'EOF'   # imports the tip tool's own binds()          -> bind_probe.out
binds('notes/*.md', 'README.md'): True   text='files under notes/ are append-only'
binds('notes/*.md', 'notes/a.md'): False  text='this file is append-only'
binds('LOG.md', 'NOTES.md'): False        text='the catalog is append-only'
binds('LOG.md', 'NOTES.md'): True         text='LOG.md is append-only'
binds('SCORE.md', 'NOTES.md'): False      text='SCORE.md is not strictly append-only'
binds('SCORE.md', 'NOTES.md'): True       text='SCORE.md is not, under any circumstances, append-only'
binds('SCORE.md', 'NOTES.md'): False      text='SCORE.md is not under any circumstances append-only'
binds('LOG.md', 'NOTES.md'): False        text='LOG.md is not append-only, and never will be'
binds('LOG.md', 'NOTES.md'): False        text="the rule here is not 'append-only'"
```

**Limit (finding).** `SCORE.md is not, under any circumstances, append-only` **binds** although a negation precedes `append-only` by three words — commas are not in the separator class of `NEG_WINDOW` (`tools/append-only-audit.py:212-213`, `(?:[\s\-]+[\w'’]+){0,3}?[\s\-]+append[- ]only`). The claim's wording ("a negation within three words before append-only unbinds") is therefore narrower than it reads: the negation must be separated by whitespace/hyphens only. Proposed fix (not applied; file frozen): widen the separator to `[\s\-,;]+` on both sides of the word run, or normalise commas/semicolons to spaces before matching. The same regex is duplicated in the frozen counter (`tools/round49-append-audit-v4-check.py:98`), so the counter's lane leg cannot catch it either. The lane's own declarations are unaffected at tip (`bad_declarations 0`).

**Verdict. ACCEPT** for the four fixtures and the lane; the punctuation case is a limit, not a refutation of the four scenarios.

**Flip condition.** Flip if a declaration that names the token as a whole word without any negation is unbound, or if the punctuation-separated negation binds in a *lane* declaration (then calibration binds a negated rule and D9 must be reworked). Note the gate may not claim "negation anywhere before append-only unbinds".

### D10 — ACCEPT `ungraded ≤ natively-exempt` per event as a bound, not a recomputation

**Claim.** For every event the tool reports, its ungraded count is at most the counter's own count of deleted lines whose parent section is an exempt title and whose origin contains an exempt title.

**Evidence.** Same two runs: tip `event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65` (tight, no slack) and base `ungraded 72 > natively exempt 65` (violated). Implementation of the check: `tools/round49-append-audit-v4-check.py:355-359`.

**Verdict. ACCEPT** as a bound. Preregistered limit: it does not recompute eligibility or the held measures (round-48 C1 territory), and the sub-20 threshold is unchanged.

**Flip condition.** Flip if the bound is satisfied with slack on an event whose launder/dated-loss fixture fails (then the bound stops discriminating), or if the counter's native count is shown to be derived from the tool's own output rather than from git history.

## Claim verdicts

| claim | target | measured at 74558c71 (my run) | at 438127bc (my run) | gate |
|---|---|---|---|---|
| C1 operability 8→8 | `witness=1 cap=1 newrow=1 witnessed=3/3 met=True` | met, exit 0 | `witness=0 cap=0 newrow=0 witnessed=0/3 met=False`, exit 1 | **ACCEPT** |
| C2 calibration 7→7 | `fixture=1 lane=1 scenarios=8/8 met=True` | met, exit 0 | `fixture=0 lane=0 scenarios=4/8 met=False`, exit 1 | **ACCEPT** |

Both counters are discriminating at the build and fail at the base. The frozen controls remain met=False (read-only): `base.c1.out`, `base.c2.out`, `junk-c1-fake-witness.c1.out`, `junk-c2-no-exempt.c2.out`, `junk-c2-word-token.c2.out`.

## What met=True does not show

Carried from the preregistration's `limits`, each confirmed relevant here:

1. C1 witnesses that the frozen binary executed as the listener with the frozen model and that its tokenizer answered a counter nonce; it does not show the binary came from the downloaded archive at replay time (the r48 replay leg's digest checks carry that), and a replay that runs the same binary from a host copy still passes the witness.
2. C1's exe check is Linux `/proc` only; a process the counter cannot read fails closed (observed: probe A/B/C all fail closed).
3. C2 origin is first appearance, so head-born text later carried in a dated section and deleted from the head again stays ungraded; identical text born in both places counts as exempt-born.
4. C2's lane leg is a bound, not a recomputation (D10).
5. Gates D1–D3 and D7: the four substitute witnesses are refused, and each refusal is grounded by a stub or a base run above, not by a reading of the docstring.

Out of scope for this seat (known integration items, not re-reported): the two round-49 counters are not yet in SKILL.md's instrument registry; SCORECARD/LOG/lesson/QUALITY/README entries for round 49 are not written; `used-by` of S494/S495 names `corpus/lessons/round-49.md`, which lands at integration.

## Reproducing

```
S=/fast/scratch/hyaku/kama-r49/S1Gate; mkdir -p "$S"; export TMPDIR="$S"
git clone -q --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
curl -sSL -o "$S/model.gguf" https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf
T=/home/vgpnk/Projects/shokunin/kama-shokunin/tools
python3 "$T/round49-replay-witness-audit.py"        --repo "$S/lane" --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch "$S/sc1r"  --out "$S/c1.out"
python3 "$T/round49-append-audit-v4-check.py"       --repo "$S/lane" --tip 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --scratch "$S/sc2r"  --out "$S/c2.out"
python3 "$T/round49-replay-witness-audit.py"        --repo "$S/lane" --tip 438127bc01ff3b99f98468549d58046f932490ef --scratch "$S/sc1b" --out "$S/c1.base.out"
python3 "$T/round49-append-audit-v4-check.py"       --repo "$S/lane" --tip 438127bc01ff3b99f98468549d58046f932490ef --scratch "$S/sc2b" --out "$S/c2.base.out"
LANE="$S/lane" MODEL="$S/model.gguf" SCRATCH="$S" OUT=<this dir> python3 gate_rejects.py
```

No tool was installed or upgraded for this seat (no pacman, no uv). The C1 counter started three llama-server processes of its own on loopback ports 44443/35935/42749 and the counter verified they were gone after reset; my probe stubs were python on ephemeral ports 47097/60809 and were killed and the ports checked to refuse (`teardown: A refuses=1 C refuses=1 B alive=0`).
