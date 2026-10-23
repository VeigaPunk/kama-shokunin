VERDICT: holds — the frozen clause (h) replayed verbatim over the round-26 shortcut set collapses it to one row (shortcut_survivors 1/12, 11 colliding pairs all against X26-01) and collapses no distinct genuine fault in the landed E26 set (e26_survivors 17/17, 0 colliding pairs; 14/14 frame-tested rows survive, 3 rows are outside the clause's reach).

Scope: X1 exploratory evidence only. Clause (h) `h:same-message-frame` of the frozen counter `.ufo/waves/round-27/count-c1.py` (sha256 `49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765`), clause lines 707-709, message extractor `error_message()` lines 506-518. Surfaces read: `.ufo/waves/round-27/a3/plan.json` (X1), `corpus/lessons/round-27.md` (claims and repairs), `corpus/knowledge/echo-discriminating-counters.md` (the rule and its two facts), `corpus/QUALITY.md:219-242` (KQ37 and its round-27 qualification). No claim is scored here, no live count was produced, no server was started, and `count-c1.py` `main()` was never run or imported.

## What the clause is (extracted, not re-implemented)

The harness reads the frozen counter, checks its sha256, and executes the clause source sliced from lines 707-708 verbatim:

```
elif (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
        fr == om.replace(oe["signature"], "\0").lower():
    clash = "h:same-message-frame"
```

Semantics preserved exactly: each side's own signature is replaced at every occurrence with one NUL; both sides are lowercased; `fr` holds the **unstripped** frame and the equality uses it, while `.strip("\0 ")` is only the "frame not blank" truthiness guard. A message equal to its own signature therefore reduces to `\0`, the guard fails, and no comparison runs. `error_message()` (lines 506-518) decodes the HTTP body and returns `error.message`; that is the `msg` the counter compares (`count-c1.py:678,686-687`). The live loop is HTTP-only (`count-c1.py:676-680`); `grep -n channel .ufo/waves/round-27/count-c1.py` returns no match.

## Command and exit

```
cd .ufo/waves/round-27/w1a3/out/ExecOfflineFrameReplay
ulimit -f 1048576 && timeout 300 python3 harness.py > run.stdout.txt 2> run.stderr.txt
exit=0   (stderr 0 bytes)
```

Trimmed stdout (`run.stdout.txt` sha256 `0490067e…090f`):

```
counter sha 49491b80e4f4ed2a85ab822a52f0b1a0fdb1dee53423e3d43b60ee25d1bf2765 pins True
frame clause extracted at lines [707, 708]: elif (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and  fr == om.replace(oe["signature"], "\0").lower():
error_message extracted at lines [506, 520]
controls all pass True
shortcut_survivors 1/12 collapsed ['X26-02'..'X26-12']
  colliding pairs: 11 (all-pairwise 66, class sizes [12])
e26_survivors 17/17 (frame-tested 14, not-applicable ['E26-15', 'E26-16', 'E26-17'])
  colliding pairs: 0 (all-pairwise 0)
  equal-frame classes ignoring guard: 1 (sizes [9], guard-suppressed pairs 36)
  signatures absent from decoded message: ['E26-07', 'E26-14']
decoded-spelling variant: e26 17/17 pairs 0 classes [11, 1, 1, 1]
raw-text counterfactual: shortcut 1/12, e26 9/17
duplicate tip receipt: e26 17/17 http-message-identical True
```

The extraction end marker `[506, 520]` is the next top-level `def`; the function body itself ends at line 518. Six controls in the harness all pass: trailing-splice frame collision fires; case-differing frame fires; distinct frames do not; `message==signature` is suppressed by the guard; repeated signature occurrences are replaced on both sides; a whitespace/NUL-only residual is suppressed.

## Set 1 — round-26 shortcut rows: 1/12

Inputs: messages decoded from `.ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/shortcut.receipt.json` (`channel_excerpt`, the full raw HTTP body: max excerpt 203 bytes, receipt lines 321-323 record registered 12 / counted 12 / met true), order from `shortcut.registry.json` (identical to receipt order; registry line 3 marks it a shortcut-control fixture).

Every one of the 12 decoded messages reduces to the same frame on both sides, frame sha256 `0776bc50464794bef8d3644fd1e446f229b9e25d8fe85b19e6bce86be82fcaea`:

```
response_format type must be one of "text" or "json_object", but got: \0
```

Colliding pairs, every collapsed row against the surviving earlier row (11 scoring pairs; 66 all-pairwise within the single class of 12):

```
X26-01 ~ X26-02   X26-01 ~ X26-03   X26-01 ~ X26-04   X26-01 ~ X26-05
X26-01 ~ X26-06   X26-01 ~ X26-07   X26-01 ~ X26-08   X26-01 ~ X26-09
X26-01 ~ X26-10   X26-01 ~ X26-11   X26-01 ~ X26-12
```

X26-01 survives because it is first in registry order, not because it is distinguishable. The count is what matters; the identity of the survivor is order-dependent.

## Set 2 — landed E26 rows: 17/17

Inputs: `registry/error-signatures-r26.json` (17 signatures) in registry order; messages decoded with the frozen `error_message()` from `.ufo/waves/round-26/final/c1-final-tip-receipt.json` (`channel_excerpt`; receipt lines 451-453 record registered 17 / counted 17 / met true). All HTTP excerpts are ≤200 bytes, below the round-26 `channel_text[:400]` truncation, so each decodes to the exact body. Replay against the duplicate `c1-tip-receipt.json` gives the same 17/17 and identical decoded HTTP messages.

No genuine collision: 0 colliding pairs, 0 all-pairwise. Composition:

- **9 rows have `message == signature`** (E26-01, 02, 04, 05, 06, 08, 11, 12, 13). Their frame is exactly `\0`; the guard suppresses the comparison. 36 pairwise comparisons are suppressed by the guard, not by frame inequality. These rows carry no residual frame at all and are separated only by the earlier `h:sub-or-superstring` / `h:shared-message` clauses (`count-c1.py:702-705`), not by clause (h).
- **5 rows have a non-blank residual**, all distinct:
  - E26-03 `unable to restore slot: \0`
  - E26-09 `\0: prefix token is missing. suffix token is missing. middle token is missing. `
  - E26-10 `input (4352 tokens) \0size (current batch size: 64)`
  - E26-07 `"input" or "content" must be provided` (cut no-op, see below)
  - E26-14 `"prompt" elements must be a string, a list of tokens, a json object containing a prompt string, or a list of mixed strings & tokens.` (cut no-op)
- **3 rows are frame-not-applicable** (E26-15, E26-16, E26-17). Their recorded channel text is process log output; `error_message()` returns `None`, so clause (h) is unreachable. They survive vacuously, not by frame discrimination.

### Two reach defects found while replaying (outside clause (h), relevant to the reviewer)

1. **Escaped registry spelling defeats the cut and the counter's own `e:not-shown`.** E26-07 and E26-14 store the raw-body spelling with literal backslash-quote (`registry/error-signatures-r26.json:159,359`); the decoded `error.message` has plain quotes, so `signature in msg` is false. Clause (h)'s `replace` is a no-op for them, and were this registry fed to the frozen counter, both rows would be refused at `e:not-shown` (`count-c1.py:686-687`) before clause (h). Re-spelling those two signatures in decoded form changes nothing for the frame rule (17/17, 0 pairs, guard class 11), so the no-collapse result does not depend on this defect — but as the registry is spelled, the counter cannot reach clause (h) for those rows.
2. **Non-HTTP rows are unreachable.** Clause (h) is fed only by `error_message()`; the counter has no channel branch and sends every row through `http()` (`count-c1.py:676-680`). 3/17 of the E26 corpus (18%) therefore lies outside the clause's reach, and their 17/17 "survival" is not evidence about discrimination.

## Sensitivity cost (reported plainly)

- **Under the exact clause: zero genuine-row collisions.** The rule removed only the shortcut class; no distinct E26 message pair shares a non-blank residual. The cost of the guard is vacuity, not over-collapse: for 9/14 frame-tested E26 rows, clause (h) can say nothing at all.
- **Counterfactual, NOT the frozen clause:** if the recorded excerpt text is used as the message instead of `error_message()` output, E26 drops to 9/17 — 8 genuine rows collapse in two classes, `{E26-01,02,04,05,08,12}` and `{E26-06,07,11,14}`, because the shared JSON envelope (`{"error":{"code":…,"message":"","type":…}}`) becomes the frame. This shows the decode is load-bearing: [INFERENCE] a replay that treats `channel_excerpt` as `msg` would wrongly report a genuine-fault cost that the frozen counter does not have.
- [INFERENCE] The rule's collapse power is exactly the shortcut's shape: a proper-substring signature spliced into an identical residual. Full-message signatures make the residual blank and the rule vacuous; a signature shared across two different templates does not collapse them. So 1/12 here calibrates the rule for this vector, not for all echo sites.

## Limits

- E26-15..17 process rows are outside clause (h); their inclusion in 17/17 is vacuous.
- The E26 rows are "appear genuine" per `corpus/lessons/round-26-verifier-spotcheck.md:118-119`, not independently proven genuine.
- No `registry/error-signatures-r27.json` exists in the lane (checked: absent), so no extrapolation to round-27 live data.
- Lowercasing is `str.lower()`, ASCII-only; all 12 shortcut and 14 E26 messages are ASCII. This matches the KQ37 qualification already recorded at `corpus/QUALITY.md:219, 221-242`.
- Clause (h) is one of seven `h:` clauses; a full-counter count is non-increasing relative to these frame-only survivors, and this replay does not apply the other six.

## Files, hashes, hygiene

- Harness: `.ufo/waves/round-27/w1a3/out/ExecOfflineFrameReplay/harness.py`, sha256 `d3c36c3ceb90ae06ddb19eb61317c48c6ac0aeb2b69c3b0fb2c94d73829c1cc5` (429 lines).
- Receipt: `.ufo/waves/round-27/w1a3/out/ExecOfflineFrameReplay/frame-replay.receipt.json`, sha256 `e4ac9b7cb7836f6e541da4962bec7790db0f58b4af4f6977772869cf584a7147`; contains extracted clause source, `error_message` source, per-row frames, all 11 shortcut collapse pairs, all 66 pairwise shortcut collisions, E26 classes, controls, and the two variants.
- stdout/stderr: `run.stdout.txt` sha256 `0490067e5a4c6b93365bd6261b87e97a49f4a9c6bd3f8b5df5cd23bb711e090f`, `run.stderr.txt` 0 bytes; run exit 0.
- Counter byte pins checked at run time: round-27 `49491b80…2765` (pinned), round-26 `6501737c…6588` (`git show eb09e742:.ufo/waves/round-26/count-c1.py | sha256sum`; copy at `/fast/scratch/hyaku/kama-r27c/ExecOfflineFrameReplay/count-c1-r26.py`).
- No server started, no port used, no model loaded. `pgrep -af llama-server` at return shows three servers on 47636/47637/47644 (ports this item was not assigned); this seat launched none, and its commands started no server.
- No tool installs or updates. No git/jj writes; only read-only `git show`/`git rev-parse`. Writes were confined to the out directory above and the /fast scratch copy.
