VERDICT: n/a — overlap scan only: ownership map, handoffs, and one bounded move; no kama claim adjudicated.

# ConnectKagi — secrets overlap scan for C1 / C2 (round 17, hyaku phase 2)

- **Seat:** connector, read-only (leaf; no subagent). Lane `kama-shokunin`; lane tip read with
  `git rev-parse master` = `cff9e62f05aa7cfb9059444f62eb787100719713`. Verified-at `2026-10-20T15:23:41Z`.
  Line refs to `tests/llamacpp-live/check-receipt.py` and `tests/probe-verdicts/check.py` are to
  the working tree at that time — both files are under active build this round, so re-grep the
  named symbols before applying the move.
- **Allowed kagi reads performed:** `kagi-shokunin/{SKILL.md,PROVINCE.md,corpus/QUALITY.md}` only.
  One `ls -la` of that repo's root (entry names/modes, no file content) preceded the three reads;
  no other path in that repo was opened or grepped.
- **Installs/updates:** none. No lane gate, harness, server or port was run; no scratch
  measurement was taken. All code claims below are static reads of the named lines.

## 0. Axes named

- **Calibration** (assigned, lowest axis at 7) — the v2 receipt is the sole durable evidence for
  the C2 verdict; it must be fail-capable about what it did *not* do as well as what it did.
- **Operability** — the live harness must stay keyless and free of operator-shell state.
- Non-harm surfaces: contract (matrix files untouched, no new check id), verification (v1 receipts
  must keep validating), substrate (kagi's own gates are currently absent, E10).

## 1. Evidence

### E1 — C2's child environment is a closed name-allowlist, and the receipt records names only

`tools/kama-llamacpp-live.py:71-72` — "the server sees only these names when present in the
harness env — names are recorded, values never are"; the tuple is `PATH, HOME, LANG, LC_ALL,
TMPDIR` (`:73`). Construction is `child_env = {k: os.environ[k] for k in CHILD_ENV_KEYS if k in
os.environ}` (`:875`) and the receipt records `sorted(child_env)` (`:876`; the pre-launch copy of
the constant is at `:843`).

This is the **correct shape** on this substrate, not merely conservative: llama.cpp gives every
server argument an environment alias. `arg.cpp` carries 156 `set_env("LLAMA_ARG_…")` calls plus
`.set_env("LLAMA_API_KEY")` (`:3542`) and `.set_env("LLAMA_ARG_API_KEY_FILE")` (`:3559`), so no
denylist of credential names is closable — an allowlist is the only finite guard. The landed
allowlist excludes both key names, which also closes the key-prefix log path by construction:
`server-http.cpp:229-234` logs `api_keys: ****%s` with the key's last four characters when exactly
one key is configured.

### E2 — the probe child gets the same allowlist

`tools/kama-llamacpp-live.py:620-621` — "Runs under the same allowlisted env as the server child
(no proxy vars can redirect it)"; enforced at `:629` (`env=child_env`). The probe is additionally
proxy-proof on its own (`tools/kama-probe.sh:294,:326` both pass `curl --noproxy '*'`), and
`--port` matrix mode is documented as having "no registry baseline" (`tools/kama-probe.sh:55`),
so dropping `UFO_SRC` from the child env does not change a C1/C2 matrix row.

### E3 — the receipt-side detector is fail-capable for an off-allowlist name

`tests/llamacpp-live/check-receipt.py:65` fixes `CHILD_ENV_ALLOWLIST = {"PATH", "HOME", "LANG",
"LC_ALL", "TMPDIR"}`; `:377-382` rejects a non-bare name ("is not a bare variable name") and an
off-list name ("child_env_keys element … is outside the allowlist"), plus a non-sorted/duplicated
list (`:383`). The mutation table already proves the detector can fail:
`mut("env-key-off-allowlist", lambda r: r["child_env_keys"].append("AWS_SECRET"))` (`:1080-1081`).

### E4 — the receipt schema docstring overstates what is recorded

`tools/kama-llamacpp-live.py:23-24` — "Only argv is recorded from the launch environment — never
env." The receipt also records `child_env_keys` (`:843`, `:876`), i.e. **env names**. The
distinction that matters is names-never-values, and that is enforced (E3); the sentence as written
is falsified by the tool's own receipt. One-line correction, C2-owned.

### E5 — argv is recorded verbatim and is the receipt's only value-bearing launch surface

`tools/kama-llamacpp-live.py:860-869` builds the whole argv (no caller-supplied flags), and
`:870` stores `receipt['argv'] = server_argv`. Every other launch-derived receipt field is a path,
digest, port, or status. So argv is the single place where a *value-shaped* secret could reach a
durable artifact if a future edit (or a forged receipt) adds a key flag.

### E6 — the current argv validator is open-set

`tests/llamacpp-live/check-receipt.py:388-421` validates `argv[0] == server.realpath`, then the
values of `-m`, `--alias`, `--host`, `--port`, `-c`, `-t`, then `tail = argv[-2:]` must be
`["--no-webui", "--offline"]` (`:420-421`). `argv_flag` returns the first match only
(`:169-176`). There is no cardinality, template, or unknown-flag check: an inserted
`--api-key <value>` between `--port` and `-c` satisfies every assertion above
**[INFERENCE — read statically; the gate was not run per the measurement rule]**.

### E7 — the cross-lane rule this violates has a name

kagi `SKILL.md:14-16` — "never print, copy, or exfiltrate a secret value, session token, cookie,
or vault field"; `corpus/QUALITY.md:24` (QA5) — "No credential material, ever". A receipt is
exactly the durable artifact those rules govern, and kama's own bar agrees:
`corpus/QUALITY.md:13` (KQ5) — "Reports contain nonsecret shape evidence only." A flag *name*
(`--api-key`) is not a secret; a flag *value* in a receipt is a copy.

### E8 — no credential is needed for either of C2's repaired surfaces

`server-http.cpp:354-359` runs `middleware_server_state` **before** `middleware_validate_api_key`,
so `/health` (and the loading 503) answer unauthenticated; kama's corpus records the same ordering
at `corpus/knowledge/endpoint-identity.md:203` — "before the API-key check (S036)". The exact
ready-body check and the loading-envelope check therefore need no key, and C2 must not acquire one.

### E9 — the reciprocal boundary is already written on both sides

kama `PROVINCE.md:40` refuses "credential material & auth flows (kagi)"; kagi `PROVINCE.md:63` —
"kama refuses to hold credentials for authenticated health checks and would route that need here
through L0". The handoff channel is L0/operator, not a direct kagi gate.

### E10 — kagi's substrate is currently absent, so the handoff cannot land in a kagi gate

kagi `PROVINCE.md:10-12` — "the janitor substrate was measured absent on this host"; the census
rows are HISTORICAL and its live gates fail `DRIFT`/`SETUP` while it is gone (`:13-17`). A C2/C1
design must not depend on a kagi-side live check this round; it may only depend on kagi's
*documented* conventions.

## 2. Contested scope

| Surface | kama's claim | kagi's claim | Ruling for this round |
|---|---|---|---|
| API-key value / auth state at a local endpoint | refuses it (`PROVINCE.md:40`) | runtime auth and credential custody (`PROVINCE.md:63`) | **Not contested.** kama must not add key support to `kama-probe.sh` or accept a key to make a check pass; any keyed-endpoint test is kagi/L0 work. |
| Exact `/health` body and loading 503 as C2 checks | kama owns the code fact (E8) | no claim | **kama owns.** Public surface, no credential, no security judgment. |
| Whether a keyed deployment is acceptable, and what pre-auth loading disclosure means | records the ordering only (E8) | risk judgment | **Report, do not adjudicate.** Name it in the round record; judgment is kagi/L0. |
| "Effective" `LLAMA_CPP_BASE_URL` when delivered through an env-ref file | file-level pin only — "code-level fallback pin, not proof of the effective environment-selected URL" (`registry/endpoint-consumers.tsv:35`) | owns `op`/env-ref resolution | **Hand off.** C2's ephemeral server is unaffected; no vault resolution in kama. |
| `~/.omp/agent/config.yml:169` (live credential) as *evidence that :168 names the auth broker* | kama documents the line and a redacting read (`corpus/knowledge/listener-census.md:225-227`) | credential custody; global config is "an attack/drift surface on janitor" (`SKILL.md:446`) | **Shared read surface, kagi's judgment.** kama may cite the key name and line number (already does: "its value is deliberately NOT reproduced"), never the value; see §4 on *how* to read it. |
| Whether an inherited credential env is a C1 calibration defect | new territory this round (§3.5) | would call it credential hygiene | **kama owns the fix; kagi supplies the rule** (names not values, no secret in a derived artifact). |

## 3. What kama must hand off rather than absorb

1. Any authenticated/keyed test of `/v1/models` or any endpoint — route through kagi via L0
   (E9). This includes "make the probe send the operator's key so a keyed server passes".
2. Any provider `apiKey`/`headers`/credential-shaped block in a consumer config: cite the pin's
   path and shape, never the block body (`SKILL.md:14-16`; `corpus/QUALITY.md:24`; `PROVINCE.md:40`).
3. Effective environment resolution via `op run` (`registry/endpoint-consumers.tsv:35`).
4. The security significance of pre-auth loading disclosure (E8): endpoint fact to kama, judgment
   to kagi/L0.
5. **Adjacent, not claimed:** `tests/probe-verdicts/check.py:274-279` spawns the (soon to be
   wrapper) probe with `subprocess.run(argv, …, timeout=PROBE_TIMEOUT)` and **no `env=`**, so the
   C1 counting command inherits the operator's whole environment — including any credential-shaped
   names — into generated wrapper scripts. The C2 surface closed exactly this (E1). This is the
   C1 item owner's call, reported here rather than proposed as my move.

## 4. Reusable conventions

- **Name-allowlist, not denylist** (kama already implements it, E1). Justified by the substrate:
  every llama.cpp server arg has an env alias (`arg.cpp`, 156 `LLAMA_ARG_*`), so denial is
  unbounded. Keep the same five-name constant in any new child (C1 wrappers included).
- **Names in durable evidence, never values** — kagi `SKILL.md:14-16` + `QUALITY.md:24`; kama's
  `child_env_keys` is the working example, and `check-receipt.py:371-385` is the machine check.
  A receipt may say `HOME`; it may not say what `HOME` was.
- **Counts-only over print-then-redact.** kagi's transcript gate is "immutable, counts-only" and
  forbids "printing matched text (`SKILL.md:44`)". kama's `listener-census.md:225` reads
  `~/.omp/agent/config.yml` with `grep … | sed -E 's/(token:).*/\1 <redacted>/'` — a *reader-side*
  redaction that leaks if the shape slips (`token:`, `token :`, `api_key:`). A `grep -c` or
  key-name-only read on the same line range yields the same non-secret fact with no leak path.
- **Refuse before reading, not after** — kagi's `POLICY` "refuses **without running**" (`SKILL.md:300`).
  The analogous receipt rule is: *reject a receipt whose argv names a credential flag before
  re-deriving any check*, so the gate's verdict never depends on evidence it should not have read.
- **No hashes of low-entropy private values.** kagi's drift gate pins six private files by mode +
  line count "because a committed sha256 of a low-entropy private file is an offline confirmation
  oracle" (`SKILL.md:220-224`). Kama's receipt hashes only public/lane bytes (server tree,
  model fixture, probe, tool), so it already complies — keep it that way if v2 grows fields.

## 5. Proposed move (one bounded)

**M1 — make the v2 receipt's `argv` a closed, credential-flag-free surface, inside
`tests/llamacpp-live/check-receipt.py`'s v2 branch (+ one mutation row).**

Concretely, when `schema == "kama-llamacpp-live/v2"`:

1. Reject any argv element that begins with `-` and matches a credential class, in either
   `--flag value` or `--flag=value` form (only flag-shaped elements are tested, so a model path
   containing `auth` is not flagged; for the two-element form the flag alone triggers rejection): `api[-_]?key`, `api[-_]?key[-_]file`, `token`, `secret`, `password`,
   `authorization`, `auth` (a superset is safe — the tool's own argv at `:860-869` matches none).
2. Require that every argv element be accounted for by the template the tool constructs from the
   receipt's own declared fields (already partially done at `:388-421`); any unaccounted element
   is a named failure rather than silently ignored. Keep template equality over `-m/--alias/
   --host/--port/-c/-t` and the `--no-webui --offline` tail as today.
3. Emit a stable reason token (e.g. `argv-credential-flag`, `argv-unaccounted-element`) so the
   fault controls and `mutants.py` can count the check, exactly as the existing `bad(...)` reasons
   are counted.
4. Add one mutation row beside `env-key-off-allowlist` (`:1080-1081`):
   `mut("argv-api-key-flag", lambda r: r["argv"].insert(2, "--api-key"))` plus its value, proving
   the new check can fail. Add the `=`-joined form as a second case only if cheap.

This is deliberately *not* a new `checks[]` id: the validator already selects a per-schema
required set (`:646-653`, "exactly {len(required)}"), so the invariant belongs in the receipt
validator, where it also protects every consumer of the receipt.

**Why non-obvious.** All three halves sit in different places: the credential rule is kagi's
(`SKILL.md:14-16`), the correct shape is kama's own C2 allowlist (E1), and the gap is visible only
by reading the *v1 validator* as an attacker would — the flag is accepted because the validator
checks named keys, never the set. The round's own counting language ("every v2 check re-derived")
does not yet include "the receipt itself is credential-free", and a green 10/10 receipt with a key
in argv would be the biggest possible overclaim this lane can produce.

**Rider (C2-owned, one line):** correct `tools/kama-llamacpp-live.py:23-24` to "Only argv and the
*names* of allowlisted environment variables are recorded — never values", so the documented
schema matches E1/E4.

## 6. Affected axes and harm check

- **Calibration (primary):** the v2 receipt becomes fail-capable on a launch surface it currently
  cannot see; a credential-bearing or extra-argument launch changes the verdict instead of passing.
- **Operability (secondary):** the harness stays keyless; no operator secret gains a path into a
  lane artifact, so a live C2 run remains runnable in any shell.
- **No harm:** the nine matrix JSON files are untouched; the verdict vocabulary is untouched; v1
  receipts keep validating because the rule is gated on `schema == …/v2`, and the v2 dispatch
  already exists (`is_v2` at `:205`, `RECEIPT_SCHEMA_V2` at `:59`, v2's check set declared at
  `:28-36`); no new check id, so the required-set count stands.

## 7. Risks

- **Pattern over-breadth.** A future legitimate flag could contain `auth`/`token` (e.g. a logging
  option). Low: the tool builds argv itself (`:860-869`); if it ever needs such a flag, the
  template rule (step 2) is the authority and the pattern can be narrowed then.
- **Forger can omit the flag.** The invariant prevents recording and naive forgery, not a
  determined forger who rewrites argv and all derived checks. `--expect-tool-sha256` pins the tool,
  not the receipt producer; state this as the bound, in kagi's style ("local receipt integrity
  only", `SKILL.md:440`).
- **Value under a benign flag.** `--alias <secret-shaped>` would still pass; `models_alias_id`
  grades it as an id, and a secret-shaped alias is domain-weird. Residual, not addressed here.
- **C1 parity.** If C1's `mutants.py` is counted as the round's calibration number, the same argv
  invariant is not in scope for the frozen 55/17 pair; do not blend the two counts.
- **Log path.** Even with argv clean, a keyed server logs its key's last four bytes
  (`server-http.cpp:229-234`). The harness's `LOG_KEEP` regex (`:66`) would not retain that line,
  and the temp log is unlinked (`:708`), but do not rely on the regex — argv closure is the
  primary guard.

## 8. Verification (L1 runs; not run by this seat)

1. `python3 tests/llamacpp-live/check-receipt.py` — selftest green, and the new
   `argv-api-key-flag` mutation is **caught** (fails as expected, counted with the others).
2. The round-16 real receipt `.ufo/waves/round-16/live/receipt.json` still validates unchanged
   (v1 path untouched).
3. A v2 receipt produced by the repaired tool validates; the same receipt with an `--api-key` flag and a
   placeholder value inserted after `--port` exits non-zero with the named reason. This is the fail-capable proof.
4. `grep -c -- '--api-key' tools/kama-llamacpp-live.py` → `0`: the honest tool remains keyless.
5. C2 counting command (`tests/llamacpp-live/controls.py`, accepted-bad before → after) unchanged
   in count unless the argv control is added there as well; if it is, record both numbers.

## 9. Limitations

- No lane gate, harness, fake server, or port was run; E6 is static inference and is labelled.
- Kagi's live substrate is absent (E10), so no reciprocal kagi check was possible; kagi's
  conventions were read from the three permitted files only.
- I did not open kagi's corpus/knowledge beyond what `SKILL.md` quotes, and did not read
  `~/.config`, `~/.omp` (beyond the rules file), or any session/transcript store.
- `check.py:274-279`'s inherited env is reported as the C1 owner's call (§3.5); it is not part of
  the proposed move and is not counted in its verification.
