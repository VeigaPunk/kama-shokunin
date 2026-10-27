# N3Pattern2 — round 50 cross-claim pattern: residual self-report acceptors

Verdict: the build extends round 49's "self-report → outside observation" move (C1: `/proc` exe/listener/maps + nonce round-trip + process tree + isolated env; C2: commit-graph birth union + CommonMark fences + CRLF keys + numstat deletion oracle) and closes round-49 routed R1, R2 and R3 — but the C2 lane leg still takes the tool's **event population and restoration half on self-report** (a tool that omits an unrestored event or labels it `restored` passes `lane=1`), while all seven instruments on the round-49 residual ranking are byte-identical at the build commit and the cheapest hatch is still digest-ledger's any-non-empty `unverifiable` note.

Axes: calibration, operability. Evidence at build commit `97c864bead3ee4a2f629574e77263d33834ec98a` (ancestor of lane HEAD `3b79eaddf38246c637cc7ba1a94ab363422876b6`), clone `/fast/scratch/hyaku/kama-r50/N3Pattern2/lane` (`git clone --shared`); base `26ecba64ad6fb571d09074b07202d1618a46ecd1`.

## Evidence

```console
$ git -C $S/lane merge-base --is-ancestor 97c864be HEAD && echo ancestor   →  ancestor
$ git -C $S/lane diff --stat 26ecba64 97c864be | tail -6
  tools/append-only-audit.py              | 157 +++--
  tools/kama-live-replay.py               |  66 ++-
  tools/kama-llamacpp-live.py             |  59 +-
  tools/round50-append-audit-v5-check.py  | 545 +++ (new)
  tools/round50-replay-bind-audit.py      | 605 +++ (new)
$ for f in digest-ledger hexrun-census gguf-identity kama-ollama-evidence \
      kama-context-capacity capability-repertoire-audit pin-trigger-consumed; do
    git -C $S/lane log --oneline 26ecba64..97c864be -- tools/$f.py | wc -l; done
  →  0 for every file (all seven untouched)
```

## Ranked: instruments still accepting a self-reported artefact after this build

Cost-to-fake × value-to-the-claim, cheapest exploit first. Line numbers re-verified on the lane working tree at build+ (`git log` shows zero commits to these files in `26ecba64..97c864be`).

**1. NEW — `round50-append-audit-v5-check.py:464,497,559-562` (against `append-only-audit.py`): the counter's lane leg consumes the tool's own `events` list and its `status`/`restored_max`/`held_at_to` fields.** `lane_leg()` iterates `j.get("events") or []` (counter :464) — events the tool chose to report — and per event checks `graded+ungraded==deleted` (:467), `deleted==numstat` (:472-475), and the v5 ungraded upper bound (:489-493). It never enumerates deletion events independently: a ≥20-line deletion the tool simply does not report is invisible to the counter, and `len(events) >= 5` (:397) passes while any 5 remain. Same for the restoration half: `exit_code` follows `status`, which derives from self-computed `restored_max`/`held_at_to` (tool :557-562); the counter reads `p.returncode == 0` (:397) but recomputes no `held(x)` — a tool reporting `status=restored` for a never-restored deletion exits 0 and passes. Cheat: a cheating `append-only-audit` drops or mislabels the unrestored event → `lane=1`. The fixtures leg does pin `status` for the 12 named scenarios (:237-300), so this hatch exists only on the lane leg — same gap shape R3 named for `ungraded` (now bounded), still open for enumeration and restoration. New surface, not disclosed in preregistration `limits` (those cover births-over-all-parents, the v4 binder copy, and the sub-20 threshold — :43-44).

**2. `digest-ledger.py:131-132` — `unverifiable` with any non-empty note (round-49 #1, unchanged).** `key = "unverifiable" if r["note"].strip() else "ledger_bad"` (:132); nothing binds the note to a checkable source. Cheat: relabel an unknown token `unverifiable` + one-word note. Still the cheapest hatch.

**3. `hexrun-census.py:273-274` — `unverifiable` note ≥ `NOTE_MIN`=10 (round-48/49 #2, unchanged; `NOTE_MIN` at :77).**

**4. `gguf-identity.py:948` + `load_receipt`/`reconcile_receipt` (:423,:644), `evidence_scope` self-labeled `receipt-self-report-not-authenticated-execution` (:629) — caller-supplied receipt accepted as reconciliation input (unchanged).**

**5. `kama-ollama-evidence.py:472-476` — `--tags`/`--ps` are caller-supplied offline captures; `loaded_same_digest` follows from a self-consistent claimant-authored pair (unchanged; honestly labeled `offline-captures-not-runtime`).**

**6. `kama-context-capacity.py:602-635` — `load_counter_cells`/`check_cells_drift` compare embedded CELLS to the registered counter's CELLS; agreement is not independent validation — a coordinated change of both passes (unchanged).**

**7. `capability-repertoire-audit.py:145-149` — evidence cell needs only a repo-relative path token that resolves at the revision (`path_exists`); nothing verifies the path substantiates the capability.**

**8. `pin-trigger-consumed.py:19-33` — committed pin-watch receipt as ground truth; `if not behind: met=True` (:30-33) means a fabricated receipt with zero `behind` rows trivially passes. Standing KQ check.**

Honourable mentions, same shape, lower value today:
- `shortcut-tally.py` — grades lane **reports** (its own disclosed `met=True`/mutant text), claimant-authored by construction; a falsifier for disclosure, not for the underlying counters.
- `manifest-crosscheck.py` — lane trend ledger vs fleet MANIFEST.json; both sides lane-authored.
- `SOURCES.md` capture files under `.ufo/waves/round-50/c1|c2/` — C1's `newrow` leg (counter `round50-replay-bind-audit.py:65-66`) requires only that the row's cells contain the man7 URL; nothing hashes the committed capture against the live URL at claim time (record-time fetch unbound — the carried K2Record gap, below).
- `kama-llamacpp-live.py` receipt `witness.waited_ms` (:373) — still self-asserted; `released` and `child_pid` are now corroborated, `waited_ms` is not.

What is **no longer** self-report (the closed legs, for contrast): rerun `child_pid` ↔ observed pid (counter :470), `witness.released` ↔ counter-created `release` + port refusing (:456,:466-468), `model_mapping` ↔ the counter's own `/proc/<pid>/maps` dev/inode + sha256 of the mapped pathname (:473-476; tool `model_mapping()` :678-725 opens the maps pathname `O_NOFOLLOW`, fstat-checks dev/inode, hashes), canary absence ↔ `/proc/<pid>/environ` + empty sitecustomize marker (docstring :30-35,:48-51), and on C2 `deleted` ↔ `git diff --numstat` and `ungraded` ↔ the counter's own birth-DAG origin count.

## Round-49 items this round closed

From `corpus/lessons/round-49-verifier-spotcheck.md` §6 (routed) and the round-49 N4Pattern list:

| Round-49 item | Status after 97c864be |
|---|---|
| R1 C1 counter gap — no pid↔`child_pid` join; PYTHONPATH/sitecustomize hijack; unbound model bytes (K1Cheat, K1Design, R0Controls) | **Yes** — invoker `python3 -I -c` + planted canaries; replay spawns live tool as `python -I` with `LIVE_ENV_KEYS` allow-list (`kama-live-replay.py` diff +307-320); `model_mapping` recorded and re-hashed (tool :678-725, replay mismatch `model-mapping:<reason>`); counter join at :470-476 |
| R2 teardown — killed counter left replay/tool/server up (X1Kill) | **Yes** — `set_own_pdeathsig()` on the replay (SIGTERM, `kama-live-replay.py` diff +91-104) plus `preexec_fn` pdeathsig on the live child (+312-317); counter snapshots the invoker's whole descendant set and requires all gone ≤30 s (docstring :60-64) |
| R3 C2 definition gaps — rev-list-order origin, fence-blind sections, CRLF-sensitive keys, unbounded self-reported `ungraded` (K2Origin F3-F5, K2Cheat, V2Ctr) | **Yes, except the binder sub-item** — birth = union over the commit graph (`sections()`/`origins()` v5; tool diff docstring), fences per CommonMark §4.5 (`fence_open`/`fence_close`), `key()` strips one trailing CR, counter re-derives `deleted` via numstat and bounds `ungraded` by its own count (counter :464-495). The counter's binder still copies the tool's v4 rule — explicitly kept as a disclosed limit, so R3's V2Ctr sub-item is carried, not closed |
| R4 surviving mutants (C1 counter 11/20, live/replay 10/23, C2 counter 16/49, v4 tool 8/29) | **No** — the build touched no mutant battery; the wave's mutation seats report separately (not a claim item) |
| R5 carried — sub-20-line deletions unwatched, prerelease cliff, b11906 population | **No** — preregistration limit: "the sub-20 threshold is unchanged" |
| R6 operator-side prompt route map (`@m_flash` vs `@m_kfc`) | **No** — operator-owned, unchanged |
| Carried from round 48 R5 — record time never fetches the URLs (K2Record) | **No** — replay fetches by content digest at replay time; the claim-time provenance of what was fetched when the receipt was written is still claimant history |
| Round-49 N4Pattern ranked residuals (digest-ledger, hexrun, gguf, ollama-evidence, context-capacity, capability-repertoire, pin-trigger) | **No** — zero commits to any of the seven files in `26ecba64..97c864be` |

## Bounded move (pattern synthesis)

The frontier move that costs least and harms no axis: extend C2's own "re-derive the fact the tool reports" discipline to the lane leg's uncovered half — enumerate candidate events independently (the counter already builds `allpar`/blob maps at :417-461; walking `git diff --numstat` over first-parent pairs for contracted files yields the event population the tool must cover, and `held(x)` is recomputable from the same blobs), so that an omitted or relabeled unrestored event flips `lane=0` exactly as a miscounted `deleted` now does. This is precisely the closure R3 bought for `ungraded`, applied to the fields R3 left self-reported. Risk: numstat/diff conventions must match the tool's (no-renames, `--text`, `-U0` already pinned at :366,:472); window semantics for `held` must match `restored_max`'s (tool :95-98,107-108) or the checker and tool disagree on restored-then-re-deleted events. Falls on calibration only; operability untouched. Verification: a mutation that drops one `events` entry or sets `status=restored` must flip lane=0 on a fixture; the existing 12 scenarios must still pass (regression).

Second-cheapest, ranked item #2/#3 combined (carried from round-49's own move): require an `unverifiable` note to cite a located, re-verifiable source (repo path, URL, revision) the tool can check, instead of any non-empty/≥10-char string.

Report: .ufo/waves/round-50/w1/out/N3Pattern2.md
