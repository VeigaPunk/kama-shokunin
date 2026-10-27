# Simp2 — YAGNI review of the round-50 build (tools/)

**Verdict:** two deletions proposed (net **−12 lines**, `6 insertions / 18 deletions`), four of the six
named candidates **retained with evidence**, one **escalated, not deleted** (provenance). The proposed
diff preserves behaviour under both frozen counters at the mutant tip — C1
`bind=1 teardown=1 newrow=1 bound=3/3 met=True`, C2 `fixture=1 lane=1 scenarios=12/12 met=True` — and
under all three tools' selftests (`AOA 36/36`, `KLR 23/23`, live tool `selftest: ok`).

Scope: `git -C <lane> diff 26ecba6 97c864b -- tools/` = 5 files / +1380 / −52. Reviewed file by file:
`append-only-audit.py`, `kama-live-replay.py`, `kama-llamacpp-live.py` (the two counters are frozen, so
findings about them are reports only).

**Provenance of every "who reads X" claim below:** the `lsp` device is **not mounted on this host**
(`read xd://lsp` → `No such tool: xd://lsp`), so caller claims are literal `grep -rn` + read of the
call site, and are labelled as such. None is presented as semantic proof.

## Axes (godspeed)

- **weight** — the proposed diff removes one unreachable branch, one silent-failure branch and one
  unread return value. Nothing on the round-50 hot path is touched: `model_mapping`, `live_env`,
  `python -I`, the allow-list and the canary surface are untouched, so no claim's mechanism moves.
- **operability** — the prctl deletion turns "silently not armed, receipt says armed" into a hard
  failure. One tradeoff (stated below), no silent behaviour change.
- **calibration** — `append-only-audit.py --json` is byte-identical before/after on the lane at two
  tips; C2 stays 12/12 with the same `ungraded_lines 89`.

## Proposed diff

`proposed-round50-yagni.diff` (applies with `git apply -p1` from the lane root), two hunks:

**H-prctl — `tools/kama-live-replay.py:92-109` and `:313-316`** — delete the `_prctl() → None` path and
the `ok` return nobody reads.

```python
def _prctl():
    return ctypes.CDLL(None, use_errno=True).prctl          # was: try/except (OSError, AttributeError) → None

def set_own_pdeathsig(sig=signal.SIGTERM):
    parent = os.getppid()
    _prctl()(PR_SET_PDEATHSIG, int(sig), 0, 0, 0)           # was: ok = prctl is not None and prctl(...) == 0
    if os.getppid() != parent: os._exit(1)                  # was: return ok   (line 109, no caller)
...
        def _child_pdeathsig():
            prctl(PR_SET_PDEATHSIG, int(signal.SIGTERM), 0, 0, 0)   # was: if prctl is not None: ...
```

Why it is a clean deletion: the None path is the *only* behaviour of the rounding. On Linux (glibc and
musl both export `prctl`) it is unreachable; off Linux it means "receipt claims
`live_child.pdeathsig: "SIGTERM"` (`:311`) while nothing was armed". `set_own_pdeathsig`'s return value
has exactly **one** occurrence in the file — its own `return ok` (`grep -n "set_own_pdeathsig\|return ok"
tools/kama-live-replay.py` → `:100` def, `:587` bare call, `:109` return). Nothing reads it.

**H-body — `tools/append-only-audit.py:476`** — delete the unreachable falsy-blob branch:

```python
-            body = r.list_lines(b) if b else []
+            body = r.list_lines(b)
```

Why it is dead: `blobs()` (`:389-399`) maps a spec to a **blob id string or None**; `body_of`'s only two
call sites are guarded — `:492` `if b is None: continue` and `:501` `if qb is not None` — so `b` is
never falsy. `list_lines()` already owns the None convention (`:403-404` `if blob is None: return []`),
so the `if b` guard is a second None convention that can never fire.

## Candidates, decided

| # | candidate | decision | evidence |
|---|---|---|---|
| 1 | `_prctl` None path (`kama-live-replay.py:92-98`, guards at `:106`, `:315-316`) | **deleted** | `prctl` exported by glibc/musl on every host where the mechanism means anything; the only effect off Linux is a false `pdeathsig: "SIGTERM"` in `:311`. C1 met=True at the mutant tip. |
| 2 | `environ_keys` (`tools/round50-replay-bind-audit.py:271`) | **retained** | it is in the **frozen** C1 counter and it is **live**: `:354` `keys = environ_keys(p)`. The `keys is None` arm (`:356-357`) is the honest "environ unreadable" path (EACCES on another uid's `/proc/<pid>/environ`), not a dead branch. Not mine to edit. |
| 3 | the `pkeys is keys` skip (`append-only-audit.py:497`, `:502`) | **retained** | measured, not assumed: mutant `pkeys = set(keys)` (skip never taken) gives **identical output** (`cmp` clean) but costs ~10 % on the lane (`1.00/0.99/0.98 s` → `1.07/1.09/1.10 s`, 330 commits, 94 files). It is the O(1) statement of "a parent holds the identical blob", it is semantics-neutral, and replacing the identity test with a bool flag is weight-neutral churn. Hazard recorded: the alias is safe only because `break` follows it — a union after it would corrupt the cached keyset. |
| 4 | duplicated `key()` / `fence_open` / `fence_close` / `sections` (tool `:275/:282/:291/:306` vs counter `:343/:305/:316/:325`) | **retained (by design)** | the C2 counter's own contract says so: "`V2Ctr` the round-49 binder copies the tool's rule (still true here: limit)". A counter that imports the tool grades the tool with itself. I diffed the two implementations: identical logic (`re.match` vs the precompiled `FENCE_OPEN` = `rb"^ {0,3}(\`{3,}\|~{3,})(.*)$"` at counter `:103`; both decode titles `b.decode("utf-8","replace").rstrip()`; both strip one trailing CR). No drift. Frozen → finding only. |
| 5 | docstring history blocks (`append-only-audit.py:31-64` "v3 (round 48) text, kept:", `:65-79` "v2 (round 47) text, kept:", 49 lines ≈ 38 % of the docstring) | **escalated, not deleted** | they are explicitly marked historical ("kept:") — my role forbids deleting marked provenance — and they are a **duplicate authority**: `SKILL.md:1453` (v2 row) and `SKILL.md:1473` (v3 row) already carry the same definitions, and a v5 row is being drafted (`T2Skill/skill.md`). The removal is prepared as `optional-docstring-history.diff` and proven behaviour-free (selftest 36/36, `--json` byte-identical), but it needs an operator/scribe decision, not a leaf seat's. |
| 6 | `res["live_child"]` (`kama-live-replay.py:311`) — my own candidate: undocumented in the module's output-key list (`:38-40`), unread by either counter (`grep -c live_child tools/round50-*.py` → 0 and 0) | **withdrawn after proof of live consumers** | `grep -rn live_child .ufo/waves/round-50` → **45 files / 107 lines** cite the field, a real reader copies it (`.ufo/waves/round-50/w1/out/X1Observe2/observer.py:515`), and three seats whose ablations *mutate* it (`J2NoPdeathsig/ablation.patch:91-99`, `J1NoEnv.md:91`, `R4Check.md:42`). Deleting it would orphan peer evidence and peer patches. It stays. |
| 7 | `body_of` falsy branch (`append-only-audit.py:476`) — my own candidate | **deleted** | see H-body; `--json` byte-identical at both tips, C2 12/12. |

No unreferenced top-level def, unused import or unused local exists in the round-50 delta: an AST sweep of
all three files reports `unreferenced=[]` and `unused_imports=[('annotations', …)]` (i.e. only the
`from __future__ import annotations` prologue). Two dead locals *do* exist in
`kama-llamacpp-live.py` (`_observe`: `ownership` at `:894`; `ready_captures`: `health_res` at `:1008`) but
both are **outside** the round-50 hunks (`@@ -678`, `@@ -1763`, `@@ -1999` positions only), so they are
recorded, not proposed.

## Evidence (all runs from `/fast/scratch/hyaku/kama-r50/Simp2`, lane clone

`git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`; mutant commit
`f9de9c61` = build `97c864b` + the two hunks, tree `49a1c97` identical to the reworded `04668a0d`)

| # | check | command | result |
|---|---|---|---|
| E1 | audit selftest, before | `python3 build/append-only-audit.py --selftest --scratch st/before` | exit 0, `AOA_SELFTEST pass=36 fail=0` |
| E2 | audit selftest, after | `python3 after/append-only-audit.py --selftest --scratch st/final` | exit 0, `AOA_SELFTEST pass=36 fail=0` |
| E3 | audit `--json`, before vs after | `… --repo lane --to <rev> --json` at `3b79ead` **and** `97c864b` | exit 0 both; sha256 identical (`055f6ff5…`, `62e3b5c6…`); `ungraded_lines 89`, `events 5` at the build tip |
| E4 | replay selftest, before / after | `python3 build/kama-live-replay.py --selftest --scratch st/before` / `after/…` | exit 0, `KLR_SELFTEST pass=23 fail=0` both (covers the `-I` + `preexec_fn` path end-to-end against a fake live tool) |
| E5 | live tool selftest (file untouched by the diff) | `python3 $S/lane/tools/kama-llamacpp-live.py --selftest` | exit 0, `selftest: ok; closed tcp6 listeners ::1:42275, ::ffff:127.0.0.1:41985` (it must run inside a lane tree: `REGISTRY` is relative to `HERE`, `:522-524`) |
| E6 | **C1 operability at the mutant tip** | `python3 <lane>/tools/round50-replay-bind-audit.py --repo $S/lane --tip f9de9c61 --scratch $S/c1f` | exit 0 — `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; `teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok`; 3/3 child_pid joined, mappings recorded |
| E7 | **C2 calibration at the mutant tip** | `python3 <lane>/tools/round50-append-audit-v5-check.py --repo $S/lane --tip f9de9c61 --scratch $S/c2f` | exit 0 — `fixture=1 lane=1 scenarios=12/12 met=True`; `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`; `dd9f5dc6… 17 <= 23`, `0718b6ab… 72 <= 72` |
| E8 | identity-skip cost | 3× each, `--repo lane --to HEAD --json` | build `1.00 0.99 0.98 s`, mutant `1.07 1.09 1.10 s`, outputs identical |
| E9 | `-I` claim in the docstring (`:48-52`) | `python3 -I <dir>/s2.py` in a dir holding a hostile `json.py` | 3.14.8: `json from /usr/lib/python3.14/json/__init__.py`; **without** `-I`: `SHADOWED`. Claim holds here; on ≤3.10 `-I` implies only `-E -s`, so the "script-dir imports" half would be false — the docstring depends on an unstated interpreter floor (≥3.11). |
| E10 | optional docstring variant | `python3 optional/aoa-no-history.py --selftest …` and `--json` at `97c864b` | exit 0, `pass=36 fail=0`; `cmp` clean against the unmodified tool |

No `llama-server` of mine is left running (`pgrep -af kama-r50/Simp2` → empty; the servers visible on the
host belong to `Sen3Teardown`, `J4Decoy`, `R0Controls2`).

## Defects / findings (exact location, command, proposed fix)

1. **`tools/kama-live-replay.py:311` + `:106` — a receipt field could assert an unarmed mechanism.**
   `live_child.pdeathsig` is written as the literal `"SIGTERM"` whether or not `prctl` was called
   (`:106` folds "prctl absent" into `ok = False`). Show it: `git show 97c864b:tools/kama-live-replay.py |
   sed -n '100,109p;305,316p'`. Fix: the proposed H-prctl — the field can now only be written on a host
   where the call is made. `J1NoEnv.md:91` records the sibling instance of this (the `isolated: True`
   self-report), so the class is already known to the wave; H-prctl closes the pdeathsig half of it.
   *Tradeoff:* off Linux the replay now dies with `AttributeError` instead of producing a receipt that
   claims a teardown it never armed. That is the one axis the change can be argued to harm; I judge a
   loud failure on a platform where the whole teardown claim is void to be the better trade.
2. **`tools/append-only-audit.py:476` — a second None convention that cannot fire** (detail above). Fix:
   the proposed H-body.
3. `kama-llamacpp-live.py:894` (`ownership = owned`, never read) and `:1008` (`health_res`, never read) —
   pre-existing, outside the round-50 diff; reported for a later seat, not proposed.

## Coordination notes for L1

- **H-prctl collides textually with a peer ablation:** `J2NoPdeathsig/ablation.patch:91-99` deletes the
  exact `_child_pdeathsig` lines H-prctl rewrites. Apply/land one, then the other; they are not
  independently applicable to the same tree.
- **H-prctl keeps `T2Skill/skill.md:11` accurate** — that drafted registry row promises "`PR_SET_PDEATHSIG`
  SIGTERM with an `os.getppid()` re-check after the prctl" and "the replay calls
  `set_own_pdeathsig(SIGTERM)` on itself": both survive verbatim.
- **`optional-docstring-history.diff` is an escalation, not a proposal** (provenance rule). If the scribe
  wants it, it belongs with the round-50 SKILL.md row, so the tool docstring stops being a third copy of
  `SKILL.md:1453/1473`.
- Nothing here changes any claim, predicate, counter, control or receipt. No lane file was edited; the
  only commit made is in my scratch clone.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/proposed-round50-yagni.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/optional-docstring-history.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/c1-final.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/c2-final.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/audit-selftest-before.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/audit-selftest-after.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/audit-docstring-only-selftest.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/replay-selftest-before.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/replay-selftest-after.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/live-selftest.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/dead-code-sweep.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/audit-json-identity.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/identity-skip-cost.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/identity-skip-alias-mutant-selftest.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/live-child-consumers.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/replay-I-isolation.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/mutant-commit.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/Simp2/evidence/mutant-commit.patch` (the exact commit C1/C2 ran on; applies with `git am` on `97c864b`)
