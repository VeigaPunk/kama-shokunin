# M5Fixture — fixture-integrity mutation test of tools/round54-cited-path-check.py

**VERDICT: 3 mutants killed, 3 survivors — including a real defect: case 15's forged-superseded assertions (tools/round54-cited-path-check.py:795-796) are DEAD CODE, unconditionally overwritten by `hit = bool(want(ok, c))` at line 810. The fixture cannot catch a counter that stops flagging forged `superseded` rows. Defect, file tools/round54-cited-path-check.py:810, fix verified in fix.diff.**

## Detector under test

`python3 <mutant> --repo $S/lane --tip 9c60eae6f7ed84f7da93d219a406aadc30958c6c --scratch $S/run_<n>`; lane read via one `git clone --shared`; tip verified `rev-parse 9c60eae6…^{commit}` = same sha. Pristine bytes at the goal commit sha256 `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` (byte-identical to the lane working tree; lane file re-hashed identical after all runs — never modified).

The self-check: `fx = (nfx == SCENARIOS)` at line 844 → `fixture=0/1 scenarios=N/15` plus per-case `fixture FAIL:` detail lines; `met = fx and lok` → exit 0/1; `could-not-evaluate` → exit 2.

## Baseline (pristine)

`logs/base.out` rc=0 — reproduces the frozen c2-build line exactly:
`fixture=1 lane=1 scenarios=15/15 cited=693 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True` (cf. `c2-build.out.receipt`).

## Mutant results

| mutant | change | run | rc | verdict |
|---|---|---|---|---|
| (a) | case-15 want literal `lambda ok, c: ok` → same lambda (comment marker only) | `logs/m_a.out` | 0 | **SURVIVED — degenerate**: the tasked weakened state IS the committed code |
| (a′) probe | smallest behavior-bearing form of (a): `hit = bool(want(ok, c))` alone decides case 15 (line 795 conjunction collapsed) | `logs/m_ap.out` | 0 | **SURVIVED — silent pass** |
| (b) | `lane2` scorecard → `"closure now \`tools/new.py\`\n"` so the forged tip cites the replacement | `logs/m_b.out` | 0 | **SURVIVED — silent pass** |
| (c) | honest `at()` ledger arg → `None` (superseded row dropped) | `logs/m_c.out` | 1 | KILLED: `fixture=0 … scenarios=14/15`, `detail: fixture FAIL: superseded re-pointed… (met=False … 'dropped': 1)` |
| (d) | `SCENARIOS = 15` → `14` | `logs/m_d.out` | 1 | KILLED: `fixture=0 … scenarios=15/14 … met=False` |
| (e) | `env = clean_env({…fixture identity…})` → `env = os.environ` | `logs/m_e_host.out` | 0 | **SURVIVED — silent pass on this host** |
| (e) benign-env probe | same file under `GIT_*`-scrubbed env + the six benign identity/config vars | `logs/m_e_benign.out` | 0 | **SURVIVED** |
| (e) poison probe | `GIT_DIR=$S/foreign/.git` added | `logs/m_e_poison.out` | 2 | KILLED only by hostile env: `could-not-evaluate: fixture repository is not the scratch directory` |
| pristine poison control | same `GIT_DIR` poison on pristine | `logs/pristine_poison.out` | 0 | `met=True` — `clean_env` neutralizes the poison (guard is load-bearing) |

## The defect — dead forged-superseded gate

`tools/round54-cited-path-check.py:795-810`:

```
                hit = bool(want(ok, c)) and ok and c["dropped"] == 0 and c["bad"] == 0 \
                    and (not ok2) and c2["bad"] == 1        # lines 795-796 — DEAD
            elif shape in ("m15", "fixed-honest"):
                …
            else:
                …
            hit = bool(want(ok, c))                          # line 810 — overwrites for EVERY case
```

`hit` at 795-796 (the only place `ok2`/`c2` are asserted) is assigned inside the `superseded` branch and then unconditionally re-assigned at 810, which runs for all cases. Case 15's effective gate is therefore `want(ok, c)` = `lambda ok, c: ok` — exactly the weakened form mutation (a) specifies. Consequences, each observed:

- **(a) is degenerate at this commit**: the fixture's real superseded gate is already the weakened lambda. (Textual no-op → `m_a` output byte-identical to baseline.)
- **(a′) survived**: removing every forged-branch assertion changes nothing — proving the assertions never execute.
- **(b) survived**: `lane2`'s tip now cites `tools/new.py`. Spy transcript (`spy.txt`, evaluate-calls captured via an instrumented run): `lane2 rev=17ace221d6 ok=True {'bad': 0, 'dropped': 0, …}` — the forged tip genuinely flips to met, yet `got` stays 15/15 because `(not ok2) and c2["bad"] == 1` is never read. In pristine, `lane2 ok=False bad=1` — the counter's check_row logic is **correct** (superseded rule at lines 461-479 demands the replacement be cited at tip); the *fixture assertion* of that behavior is dead. Coverage hole in the self-check, not a counter-logic bug — but it means a counter weakened to no longer flag forged `superseded` rows would print `scenarios=15/15` anyway.
- `lane2 = evaluate(...)` at line 794 still runs every run — observable cost paid, result discarded.

## (e) regime analysis

Host env had `GIT_EDITOR=true GIT_PAGER=cat GIT_TERMINAL_PROMPT=0` (benign) and a global `user.name`/`user.email`. With `env = os.environ` the fixture inherits those plus the host global git identity → commits succeed → identical 15/15 output. Detection is purely environmental: `GIT_DIR` redirection gets caught by the fixture's own toplevel/`--absolute-git-dir` verification (`fixture repository is not the scratch directory`, exit 2 — could-not-evaluate, not a met verdict), and pristine under the same poison still passes. So (e) survives silently in benign environments; no intrinsic self-check for the guard's presence.

## Proposed fix (verified)

`fix.diff` — hoist `hit = bool(want(ok, c))` into the `m15`/`fixed-honest` and `else` branches so the `superseded` branch's richer `hit` stands:

- `fix_pristine.py` (fix on pristine): `logs/fix_pristine.out` rc=0, `scenarios=15/15 met=True` — honest lane still met.
- `fix_on_mutb.py` (fix + mutant-b): `logs/fix_on_mutb.out` rc=1, `fixture=0 scenarios=14/15`, `fixture FAIL: superseded re-pointed citation discloses, forged superseded is bad` — the survivor is killed.

Note: `fleet=` rev differed between the first battery (`666bc1e`) and the fix runs (`e1b4c8f`) — fleet HEAD advanced mid-run; both runs are internally consistent (fleet counts 693/14/14 throughout), lane measurement unchanged.

## Restoration & hygiene

Every mutant reverses to pristine bytes exactly (per-mutant reverse-substitution → sha256 `d70a1729…`, verified for all six). Lane file sha256 unchanged pre/post; `git status --porcelain` on the counter file empty; `pgrep -af llama-server` → none. No tooling installs needed (python3 3.14.8, git 2.56.0 already present). Scratch `/fast/scratch/hyaku/kama-r55/w1/M5Fixture` (incl. the shared clone) removed after staging.

## Files

- `mut_{a,ap,b,c,d,e}.py`, `fix_pristine.py`, `fix_on_mutb.py`, `fix.diff`, `spy.txt`, `logs/`, `c2-build.out.receipt` — all under `.ufo/waves/round-55/w1/out/M5Fixture/`.

Report: .ufo/waves/round-55/w1/out/M5Fixture.md
