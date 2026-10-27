# X04EnvNames — live-child env_leg enumeration (C1, kama round 56)

**Verdict: the C1 detection path reproduces exactly on a live child, and the whole delta is
the one `BAD_ENV` member.** With `LD_AUDIT=/usr/lib/libexpat.so.1` at exec time,
`env_leg` of the round-55 counter (`tools/round54-replay-code-audit.py`, sha256
`c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af`) returns 269 variable
names and an empty problem list — `ld_audit=missed`, exit 0; `env_leg` of the round-56
counter (sha256 `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f`, equal to
`preregistration.json` `claims.C1.counter_sha256`) returns the same 269 names and exactly one
problem, `env: server environment carries LD_AUDIT` — `ld_audit=detected`, exit 0. The two
`env_leg` and `environ_keys` bodies are byte-identical between the counters (AST extraction):
the only functional change is `BAD_ENV` gaining `"LD_AUDIT"`
(`tools/round56-replay-code-audit.py:147` vs `tools/round54-replay-code-audit.py:146`).
Detection is exact-name membership over the **exec-time** `/proc/<pid>/environ` block; values
are never read. Two calibration defects are measured below (D1 harness single-bit collapse,
D2 claim/battery expectation-direction mismatch); neither falsifies C1's target fields, both
are text/assertion-precision defects. No least-privilege surprise: no `llama-server`,
`kama-llamacpp-live` or `kama-live-replay` process was ever started.

Seat: X04EnvNames (leaf). Lane: kama. Lane tip under test:
`efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (the round-56 freeze commit; the tree on disk
matches it — counter digest above recomputes from the lane file). Host Linux 7.2.11-arch1-1,
Python 3.14.8, glibc with `rtld-audit` refusing a non-audit DSO (below). No lane file was
written except this report and `.ufo/waves/round-56/w1/out/X04EnvNames/`; jj state, Git
index, fleet root, sibling lanes and `shokuknow` untouched; no `pacman`, no tool install, no
`git add`/`commit`/`reset`.

## 1. What I ran

Read-only imports plus two committed harness invocations, all from my scratch
(`/fast/scratch/hyaku/kama-r56/X04EnvNames`, `TMPDIR` set to it):

```
python3 tools/round56-env-leg-test.py --counter tools/round54-replay-code-audit.py  --expect missed
python3 tools/round56-env-leg-test.py --counter tools/round56-replay-code-audit.py  --expect detected
python3 probe-envleg.py      # 6 live sleep children + 2 unreadable-pid cases, env_leg of both counters
python3 setenv-probe.py      # child that setenv()s LD_AUDIT after exec
```

Exact outputs (`X04EnvNames/harness-round55_counter.out`,
`X04EnvNames/harness-round56_counter.out`):

```
ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.
ld_audit=missed pid=1892836 problems=[]
exit=0

ERROR: ld.so: object '/usr/lib/libexpat.so.1' cannot be loaded as audit interface: undefined symbol: la_version; ignored.
ld_audit=detected pid=1892839 problems=['env: server environment carries LD_AUDIT']
exit=0
```

`probe-envleg.py` does not use the harness: it spawns `/bin/sleep 20` itself with a
controlled `extra` environment, reads `/proc/<pid>/environ` raw (bytes, names, the exact
`LD_AUDIT` entry), then calls each counter module's own `env_leg(pid, probs)` and compares the
returned sorted key list with the raw name list. Process hygiene: every child was
`terminate()`d and `wait()`ed in a `finally`; `pgrep -af llama-server` returned 0 both before
and after, and `pgrep -af "sleep 20"` returned 0 after.

## 2. Enumeration (8 cases × 2 counters)

Full machine copy: `X04EnvNames/envleg-enumeration.tsv` (sha256
`182878bc6f62d308592f1c3a58acbce2ee78f3bd4d3fc4c27bf40b551bb4afb8`), raw JSON in
`X04EnvNames/probe-envleg.json`.

| case | names | audit-shaped names seen | r55 `LD_AUDIT` in keys / problems | r56 `LD_AUDIT` in keys / problems |
|---|---|---|---|---|
| `LD_AUDIT=/usr/lib/libexpat.so.1` | 269 | `LD_AUDIT`, `npm_config_audit` | yes / `[]` | **yes / `env: server environment carries LD_AUDIT`** |
| `LD_AUDIT=` (empty value) | 269 | `LD_AUDIT`, `npm_config_audit` | yes / `[]` | **yes / `... carries LD_AUDIT`** |
| `LD_AUDITX=/usr/lib/libexpat.so.1` | 269 | `LD_AUDITX`, `npm_config_audit` | no / `[]` | no / `[]` |
| `KAMA_X04=LD_AUDIT` (name in value) | 269 | `npm_config_audit` | no / `[]` | no / `[]` |
| `ld_audit=...` (lowercase) | 269 | `ld_audit`, `npm_config_audit` | no / `[]` | no / `[]` |
| clean child | 268 | `npm_config_audit` | no / `[]` | no / `[]` |
| pid 999999 (nonexistent) | unreadable | — | `None` / `env: environ of pid 999999 unreadable` | `None` / same |
| pid 1 (foreign uid) | unreadable | — | `None` / `env: environ of pid 1 unreadable` | `None` / same |

Every row where `/proc/<pid>/environ` was readable had `keys == sorted(raw_names)` for **both**
counters — the returned list is the complete name inventory, not a filtered one.

Read in order:

1. **The target's two field values are exact.** `ld_audit=missed` / `exit=0` for the
   round-55 counter and `ld_audit=detected` / `exit=0` for the round-56 counter, on the same
   live-child vector as the frozen receipt (`measured/base-c1.out`, `measured/build-c1.out`).
2. **The old counter's env leg is not broken — it is specific.** In a single child carrying
   both `LD_PRELOAD=/nonexistent/kama-x04.so` and the audit variable (270 names), r55 reports
   only `... carries LD_PRELOAD`; r56 reports `LD_PRELOAD` **and** `LD_AUDIT`. So the r55 miss
   is a missing name in `BAD_ENV`, not a dead leg, and the r56 member is additive (no other
   member changed: `BAD_ENV` r54 = `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES")`, r56 =
   `("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")`).
3. **Name-only, exact, case-sensitive.** Empty `LD_AUDIT=` is still flagged (the name is the
   signal, so a producer cannot evade by blanking the value); `LD_AUDITX` and `ld_audit` are
   not flagged (correct: `ld.so` reads the exact uppercase name — case-sensitivity is not a
   false-negative channel in practice); a value that *contains* the string is not flagged,
   matching the docstring "values are never read". `npm_config_audit` sitting in every child
   (the honest shell environment is wide — this seat inherits it) produces no problem in
   either counter, i.e. no substring false positive against the real world.
4. **Detector scope is the exec-time block, and that is the right scope.** A child that
   `setenv("LD_AUDIT", ...)` **after** exec shows the name in its own `os.environ` (269 names,
   `has_LD_AUDIT=True`) but not in `/proc/<pid>/environ` (`has_LD_AUDIT=False`, 14,026 bytes);
   `env_leg` reads the `/proc` side (268 keys, no problem) — `X04EnvNames/setenv-edge.out`.
   `ld.so` resolves `LD_AUDIT` once, during program start-up, so a later `setenv` cannot cause
   loader injection; the blindness is semantically correct rather than a gap. The vector the
   counter must see — a producer that puts the name into the environment **at exec** — is
   exactly the one it sees (§2 row 1, and the `K1Cheat` producer-mutation model).
5. **Scope of the evidence.** With this value the loader refuses the object
   (`cannot be loaded as audit interface: undefined symbol: la_version; ignored`), so the
   measurement is about *name classification*, never about an audit DSO loading —
   consistent with `preregistration.json` `limits`. I make no injection claim.

## 3. Defect D1 (calibration, minor) — the harness collapses "unreadable" into "missed"

`tools/round56-env-leg-test.py:26`

```python
detected = keys is not None and any("LD_AUDIT" in x for x in probs)
```

When `environ_keys` fails, `env_leg` returns `None` **and** appends a problem; the harness
discards that problem and prints `ld_audit=missed`, i.e. bit-identical to a clean environment.
Measured with a 4-line stub counter whose `env_leg` returns `None` and appends
`env: environ of pid N unreadable` (`X04EnvNames/stub-unreadable-counter.py`):

```
ld_audit=missed pid=1905670 problems=['env: environ of pid 1905670 unreadable']   exit=0  (--expect missed)
ld_audit=missed pid=1905673 problems=['env: environ of pid 1905673 unreadable']   exit=1  (--expect detected)
```

The frozen **counter** is fail-closed here, so C1's target is unaffected: its envnames leg
passes only on `not eprobs and envnames is not None`
(`tools/round56-replay-code-audit.py:796,825`), and an unreadable environ puts a string in
`eprobs`, so the leg fails and `met=False`. The soft spot is the battery harness's single bit.
Proposed fix (text-only, no predicate change): print a third outcome, e.g.

```python
if keys is None:
    print(f"ld_audit=unreadable pid={p.pid} problems={probs}")
    return 2
```

and keep `--expect` accepting only `detected|missed` so an unreadable result can never satisfy
either leg. This round's frozen receipts (`problems=[]` with 269 keys) are unaffected.

## 4. Defect D2 (calibration, minor) — claim wording names the opposite assertion direction

C1's target says the mutant "misses it so the battery's expected-detected assertion fails".
The committed battery does not run the mutant that way:
`tools/round56-env-leg-battery.py:18,50` gives `m-drop-ldaudit` the roster field
`{"designation": "kill", "expected": "missed"}` and invokes `run(..., "missed", ...)`, so
`measured/m-drop-ldaudit.out` correctly ends `ld_audit=missed ... exit=0` and the battery
prints `pass` for its kill leg.

Measured on the same one-line mutant (`BAD_ENV` loses `LD_AUDIT`,
`X04EnvNames/harness-mutant-expect-*.out`, mutant sha256
`a3faaf6ea4c0ec0a4232d1a96da8e351d5584c0e116d9707e61e4342f364ddb4`, unique anchor asserted):

| mutant invocation | result | exit |
|---|---|---|
| `--expect detected` (the claim's wording) | `ld_audit=missed problems=[]` | **1 — expected-detected assertion fails** |
| `--expect missed` (what the battery commits) | `ld_audit=missed problems=[]` | 0 |

So the kill is real and discriminating — a mutant that still detected would fail the
committed `expected=missed` leg (line 30: `ok = p.returncode == 0 and fields.get("ld_audit") ==
expected`) — but the sentence in `preregistration.json` / the wave claim names an
`expected-detected` assertion that the battery never makes. Proposed fix: replace the clause
with "…misses it so the battery's kill leg (expected `missed`) fails if the mutant still
detects, and `--expect detected` exits 1", or freeze the mutant leg as `expected: detected`
in the roster. Not a predicate change and not a C1 falsifier; it is the sort of wording/code
mismatch K05PredicateIdentity is chartered to find, surfaced here because the receipts are in
my hands.

## 5. Frozen digests measured by this seat

| file | sha256 | vs frozen |
|---|---|---|
| `tools/round56-replay-code-audit.py` | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` | **equal** to `claims.C1.counter_sha256` |
| `tools/round54-replay-code-audit.py` (round-55 baseline) | `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` | equal to round-55 `claims.C1.counter_sha256` |
| `tools/round56-env-leg-test.py` | `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` | (no frozen digest; recorded for replay binding) |
| `tools/round56-env-leg-battery.py` | `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` | (no frozen digest; recorded) |

## 6. Risks and limits of this seat's evidence

* **Environment width.** The harness inherits this shell's environment, so its children carry
  268–270 names; the honest `llama-server` carries 5. Absolute counts here must not be read as
  the server's inventory — the discriminating observations are name presence and the
  `problems` list, both of which are width-independent. The counter's real envnames leg still
  runs against the scrubbed child (`envnames b1: 5 environment variable names recorded` in the
  round-55 control receipt).
* **Not exercised here** (other seats / other rounds): the 3/3 replay binding, the code leg,
  `HOST_LIBS` basename admission (round-55 J5 fix B, not part of this round's frozen claim),
  and whether an audit DSO exporting `la_version` loads on this glibc. None is claimed.
* **Battery not re-run end-to-end** because it writes `OUT = lane/.ufo/waves/round-56/measured`
  and the lane is read-only for seats; I exercised its exact components (same harness, same
  one-line mutant text, same expectations) in scratch instead. X01ReplayC1 owns the end-to-end
  rerun.
* A mutant/driver copy lived only in scratch and was removed; the receipts are the copies in
  the output directory.

## 7. Files written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-56/w1/out/X04EnvNames.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-56/w1/out/X04EnvNames/`:
  `probe-envleg.py` (`c0ea407dcfcedea58850b40d431d7f4ef01c041d36816c99719fcb14ee90af8d`),
  `probe-envleg.json` (`12f05e0970352dc18e74e4a3ed86de1f3006402f477e6631c41e1a3a559cce27`),
  `envleg-enumeration.tsv` (`182878bc6f62d308592f1c3a58acbce2ee78f3bd4d3fc4c27bf40b551bb4afb8`),
  `harness-round55_counter.out` (`8a1dc0ade3e371f9d59e060ab847d5bbb62a01ebf6c268d4c5a873fc1c8520c9`),
  `harness-round56_counter.out` (`80e869d4919a504bf6feb97d77f2250872b7cbf31df66719d48701fb7a18ef41`),
  `harness-mutant-expect-detected.out` (`9b37da953e7aba5dbde81fd7e67093854d3e8cc09f53883f0ff81a55480329ca`),
  `harness-mutant-expect-missed.out` (`7b42b5404503895e50044e1073ec608746fee9c0f320917b83f4cb88ff5f3230`),
  `harness-stub-unreadable-expect-missed.out` (`5fcc75998d66668f66aaaa8cb58a3316c2e81352aa4b5390e920eb2c5b1fa82a`),
  `harness-stub-unreadable-expect-detected.out` (`2d91ad9fcb5fcc0f57c91663200d388eb31b68f330d5e6dd1e04d47ae46dc96c`),
  `stub-unreadable-counter.py` (`0db209e559550e130cd62bd825862460dd8dfdf9009781338ba298c9b231de54`),
  `setenv-probe.py`, `setenv-edge.out` (`065300959d930e39b9a1fbfefbcfece9b224ed213ce1509c896a9bebc8f1e84d`).

Scratch `/fast/scratch/hyaku/kama-r56/X04EnvNames/` removed before yielding; `/tmp` unused.
