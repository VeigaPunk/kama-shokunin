# X1Nonce — round 49 nonce robustness (lane kama, C1 operability)

**Verdict:** C1's nonce witness is flake-free for the form it actually sends — 30/30 fresh
`kama witness <16 hex>` nonces in the assignment run, 300/300 in a bulk run plus 16/16
homogeneous-hex nonces, and the frozen `observe()` itself returned `problems=[]` on a fourth
held server. Four witnessed reruns of `receipt-3.json` all matched, all recorded
`witness.released true`, and every server was gone afterwards. **But** the vocabulary-literal
half of the rule (`tools/round49-replay-witness-audit.py:280-281`) is unsound for content that
tokenizes to a `<0xXX>` byte-fallback entry: a trailing newline, a tab, `\x01` and CJK `中` all
fail the `pieces` check while `/detokenize` round-trips them exactly. That class is structurally
unreachable from the frozen nonce alphabet, so this is a scoping caveat plus a two-function fix
(F1), not an operability defect in C1 as shipped.

## 1. What was held

Four separate witnessed holds of the round-48 receipt
`.ufo/waves/round-48/c2/live/receipt-3.json`, each through the lane's own
`tools/kama-live-replay.py --witness-dir D` run from a `git clone --shared` of the lane at
`74558c71c38ceaeace15fd4cf8aa9d84977584b1` (scratch only; the lane itself was never written).
Each hold: `D/ready.json` (`kama-live-witness/v1`) announced the replay's llama-server child,
my probe read `/proc/<pid>/exe`, the LISTEN inode, `/proc/<pid>/cmdline` and the model, sent its
tokenize/detokenize traffic, wrote `D/release`, and the replay tore the server down.

| run | purpose | pid / port | witness waited | assertions | replay |
|---|---|---|---|---|---|
| 1 | 30 counter-form + 10 edge | 304512 / 34105 | 300 ms | exe sha256 == frozen `35ac50fb…7ff0`; LISTEN inode owned by pid; `/health` ok before+after; `-m` frozen | exit 0, `match: true`, 0 mismatches |
| 2 | call the frozen `observe()` itself | 362860 / 38757 | 150 ms | `observe()` found no problems (exe/listen/model/nonce all clean); `/health` ok | exit 0, `match: true` |
| 3 | localise the failing half of the rule | 428656 / 38075 | 100 ms | `/health` ok | exit 0, `match: true` |
| 4 | 300 counter-form + 16 homogeneous + 10 edge | 519139 / 45355 | 2104 ms | `/health` ok | exit 0, `match: true` |

Every run: rerun receipt `outcome: pass`, `witness.released: true`, teardown `returncode: 0`
and `port_refuses: true`; after release `/proc/<pid>` is gone and the port refuses
(`evidence.json` → `runs`). No llama-server of mine survives; `pgrep -f kama-r49/X1Nonce` is
empty.

`observe()` on run 2 (direct, unmodified frozen function):
`nonce = "kama witness 1965a9036cedc54c"`, `problems = []`, detok
`" kama witness 1965a9036cedc54c"`, ids `[409, 314, 412, …]` (`evidence.json` →
`observe_direct`).

## 2. The counter's own form — 30 + 300 + 16, no failure

Rule applied verbatim: `piece` must be a `str`, `0 <= id < len(vocab)`, and
`vocab[id].replace("\u2581", " ") == piece`; then `/detokenize` of those ids must equal
`nonce` or `" " + nonce` (`tools/round49-replay-witness-audit.py:278-286`). Every check below
evaluated `True` as a whole.

| sample | nonces | rule holds | token count per nonce | detok form |
|---|---|---|---|---|
| fresh `secrets.token_hex(8)` suffixes, run 1 | 30 | **30 / 30** | 23–25 | `" " + nonce` 30/30, exact nonce 0/30 |
| fresh suffixes, run 4 | 300 | **300 / 300** (1.89 s total) | 22–25 | exact nonce 0/300 |
| homogeneous `c*16` for all 16 hex chars | 16 | **16 / 16** | 25 (digit suffixes), 24 (letter suffixes) | `" " + nonce` |

Why it is structurally flake-free on this model, not just lucky: the nonce alphabet is
`k a m space w i t n e s s space` + `[0-9a-f]`. In the frozen 512-entry
`tokenizer.ggml.tokens` every one of those characters has a real token (`0`→id 477, `a`→412,
`k`→433, `f`→431, …, and the space before the suffix is the bare boundary token
`▁`→id 410, since no literal `" "` entry exists), and the ▁-prefixed letters exist too (`▁k`→409, `▁w`→263,
`▁a`→261 … `▁f`→272; `▁0`…`▁9` do not, which is why letter-suffix nonces carry one token
fewer). The 256 byte-fallback entries are ids 3–258 (`<0x00>`–`<0xFF>`); none of the 30
counter-form tokenizations recorded with ids touches one, and the other 300 bulk nonces held
under the same predicate, which no byte-fallback piece can satisfy
(`evidence.json` → `counter_form`, `offline_comparator_test.fallback_records`). The first
token of every counter-form nonce is `▁k` (id 409), which is exactly why the detokenized text
carries the single leading space.

## 3. The ten edge forms (run 1 and run 4 agree form-for-form)

| # | form | len | tokens | rule | stage |
|---|---|---|---|---|---|
| 0 | `kama witness 0123456789ABCDEF` (uppercase hex) | 29 | 25 | holds | ok |
| 1 | `KAMA WITNESS 0123456789abcdef` (uppercase words) | 29 | 30 | holds | ok |
| 2 | `kama witness 0123456789012345` (digits only) | 29 | 25 | holds | ok |
| 3 | ` kama witness 0123456789abcdef` (starts with a space) | 30 | 26 | holds | ok — detok is `"  kama…"` (two spaces), accepted only by the `" " + nonce` branch |
| 4 | `kama witness ` + `a`*187 (200 chars) | 200 | 195 | holds | ok |
| 5 | `kama witness ` + `0`*200 | 213 | 209 | holds | ok |
| 6 | `kama witness café0123456789ab` (non-ASCII é) | 29 | 24 | holds | ok — `é` is a real vocab token (id 485), no fallback |
| 7 | `kama witness 0123456789abcdef\n` (newline) | 30 | 26 | **FAILS** | `pieces` |
| 8 | `kama witness ` (empty suffix) | 13 | 9 | holds | ok |
| 9 | `kama witness 0123456789abcdef0` (17 hex, one long) | 30 | 26 | holds | ok |

## 4. F1 — the `pieces` predicate is unsound for `<0xXX>` byte-fallback tokens

**Where:** `tools/round49-replay-witness-audit.py:280-281` (the `bad` comprehension) and the
docstring claim at `:45-51` ("every returned piece equals the counter's own decoding of
`tokenizer.ggml.tokens[id]` … U+2581 read as a space").

**Command that shows it** (in my scratch, against a held rerun — `probe_depth.py`, re-runnable):

```
newline : pieces_rule_holds False, detok_rule_holds True, bad [{"id": 13, "piece": "\n", "vocab": "<0x0A>"}]
tab     : pieces_rule_holds False, detok_rule_holds True, bad [{"id": 12, "piece": "\t", "vocab": "<0x09>"}]
0x01    : pieces_rule_holds False, detok_rule_holds True, bad [{"id": 4,  "piece": "\u0001", "vocab": "<0x01>"}]
CJK 中  : pieces_rule_holds False, detok_rule_holds True, bad [{"id":231,"piece":[228],"vocab":"<0xE4>"},
                                                             {"id":187,"piece":[184],"vocab":"<0xB8>"},
                                                             {"id":176,"piece":[173],"vocab":"<0xAD>"}]
control : pieces_rule_holds True,  detok_rule_holds True
```

So for a byte-fallback id llama.cpp renders the *byte*, not the vocabulary string: `"\n"`, and
for bytes that are not valid UTF-8 a **JSON array of ints** (`[228]`, `[184]`, `[173]`), which
the `isinstance(..., str)` guard also rejects. A correct server therefore trips
`probs.append("tokenize pieces disagree…")` (`:283`) and `witness_one` returns `False` — the
whole C1 leg would report `met=False`. The detok half of the rule passes in all four cases, so
the failure is purely the vocabulary-literal comparison.

**Reachability:** zero for the frozen nonce (section 2). This is a latent false-positive class
only if the nonce form, the model, or the rule's scope changes; the rule as *written in the
docstring* is broader than what it validates.

**Proposed fix** (`proposed-c1-piece-rule.diff` in the out directory, applies to
`74558c71…`): add `piece_want()`/`piece_matches()` beside `observe()` and replace the
comprehension with `bad = [t for t in tk if not piece_matches(t, vocab)]`. Byte-fallback
entries are expected as their byte (str encoded UTF-8, or list of ints); every other entry
stays `tok.replace("\u2581", " ")`. The patched file compiles (`python3 -m py_compile` → ok).
Evaluated offline over all 45 captured token/id records (40 from run 1 + 5 from run 3): the
current predicate rejects 5 records, the proposed one rejects 0, and four negative controls
(mutated piece, shifted id, out-of-range id, fallback piece rendered as a space) are all
rejected — `counter-rule-offline-test.json`.

## 5. F2 (bounded note) — `dt in (nonce, " " + nonce)` never exercises its first branch

For this model the detokenized form is always `" " + nonce` (0/330 exact matches; the leading
space is the `▁k` rendering, not an added token). The `nonce` branch is dead here, and the
`" " + nonce` branch cannot distinguish the expected single leading space from a doubled one:
edge 3, whose nonce already starts with a space, round-trips to `"  kama…"` and is accepted.
Unreachable from the frozen form (it never starts with a space), so no flake and no action
needed; if the nonce form is ever widened, `dt == " " + nonce` is the invariant to assert.

## 6. Limits

- Four holds, one model (stories260K, 512-entry vocab), one receipt, b11909. Nothing here speaks
  to other vocabularies or to a byte-fallback-free model.
- Run 3 did not re-check `/proc/<pid>/exe`; the run-1 and run-2 evidence covers the identity
  checks (run 2 through the frozen `observe()`).
- The replay's informational `notes` line differs from the round-48 receipt
  (`tool.sha256: 1e5ea0… -> 72e760…`): the lane's live tool now carries `hold_for_witness()`,
  which is exactly the round-49 build. The counter does not compare `notes`, and both reruns
  matched.

## 7. Reproduction

```
S=/fast/scratch/hyaku/kama-r49/X1Nonce; export TMPDIR=$S
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C $S/lane checkout 74558c71c38ceaeace15fd4cf8aa9d84977584b1
cd $S && python3 probe.py        # run 1: 30 + 10
python3 confirm.py               # run 2: frozen observe()
python3 probe_depth.py           # run 3: newline/tab/0x01/CJK localisation
python3 probe_bulk.py            # run 4: 300 + 16 + 10
python3 offline_test.py          # comparator test, no server
```

Each driver starts the held server only through `kama-live-replay.py --witness-dir`, downloads
≈22 MB (server archive) + 1.2 MB (model), and releases it before exiting. No tool was installed;
nothing was written outside this scratch and the out directory.

## 8. Artifacts (`.ufo/waves/round-49/w1/out/X1Nonce/`)

`evidence.json` (consolidated, with per-artifact sha256), `probe-result.json` (run 1 raw,
including every nonce, ids, pieces, detok), `observe-confirm.json`, `nonce-depth.json`,
`nonce-bulk.json`, `counter-rule-offline-test.json`, `replay-run1.json`, `replay-run4.json`,
`rerun-receipt-run1.json`, `rerun-receipt-run4.json`, `ready-run1.json`, `replay-run1.log`,
`probe.py`, `confirm.py`, `probe_depth.py`, `probe_bulk.py`, `offline_test.py`,
`proposed_piece_rule.py`, `proposed-c1-piece-rule.diff`.
