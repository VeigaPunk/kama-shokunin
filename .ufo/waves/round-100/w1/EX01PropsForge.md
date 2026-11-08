# EX01PropsForge — C2 probe forgery battery (round 100, wave 1)

**Seat:** EX01PropsForge. **Assignment:** build probe forgeries for C2 and grade them through the
frozen counter's public path; name any mutant that VIOLATES the claim's wording
('reads the body only on a final HTTP 200') yet exits 0 as a counter blind spot.
**Claim attacked:** C2 only (depth). C1 was not attacked by this seat (out of assigned scope);
its verdict line at the end is included for completeness and marked neutral/not-attacked.

**Frozen inputs (all read-only):**

- Plan: `plans/round-100-claims.md` (C2 §, lines 75–113)
- Counter: `tools/round100-props-status.py` (221 lines; cells at lines 72–83)
- Probe at M: `tools/kama-probe.sh` @ `2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`, `router_autoload()`
  at lines 898–928, gate line 904
- Base: `6776c667372a0da8635ebfbda6cbc92d8fb17304`
- Committeed receipts: `.ufo/waves/round-100/measured/c2.out`,
  `controls/c2-base.out`, `controls/c2-candidate.out`, `controls/c2-mutant-blanket.out`

**Tooling:** no installs needed, no toolchain added. `python3`, `curl` 8.23.0, `bash` 5.3.20
(M probe syntax verified: `bash -n tools/kama-probe.sh` → OK). No pacman, no sudo, no writes
outside `w1/out/EX01PropsForge/`, `w1/EX01PropsForge.md`, `/fast/scratch/hyaku/kama-r100/EX01PropsForge/`.
No tracked lane file edited by this seat (see §6 quarantine note on two sibling-modified files).

**Method (exact command per mutant):**

```
python3 tools/round100-props-status.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --rev 2e27e6f1 --probe-file <mutant> --work /fast/scratch/hyaku/kama-r100/EX01PropsForge/work-<id>
```

Each mutant = `git show 2e27e6f1:tools/kama-probe.sh` bytes with ONE documented change to
`router_autoload()` (see §2). Unmodified copy re-graded as a sanity oracle. Sources:
`probe-*.sh` + `probe-*.out.txt` in `.ufo/waves/round-100/w1/out/EX01PropsForge/`; maker/runner
`run_mutants.py` in the same dir (copied from scratch per the no-foreign-edit rule).

## 1. What the counter actually grades (read before forging)

Counter cells (`tools/round100-props-status.py:72-83`): nine live loopback stub cells, each a
`(status, body, extra-headers)` triple on `GET /props` with a 200 `/v1/models` carrying one
`unloaded` entry. Graded triple is `(verdict, reason, exit)` from `bash probe check … --json`:

| cell | stub answer | want |
|---|---|---|
| S1-401-router-off | 401 + `{"role":"router","models_autoload":false}` | UNREAD (router-autoload-unread) |
| S2-500-router-on | 500 + `{"role":"router","models_autoload":true}` | UNREAD |
| S3-503-router-off | 503 + router-off | UNREAD |
| S4-403-router-on | 403 + router-on | UNREAD |
| S5-202-router-on | 202 + router-on | UNREAD |
| S6-302-router-on | 302 + Location:`/elsewhere` + router-on | UNREAD |
| S7-401-llamacpp | 401 + llama.cpp `Invalid API Key` error doc | UNREAD (stable) |
| P1-200-router-off | 200 + router-off | OFF (router-unloaded) |
| P2-200-router-on | 200 + router-on | ON (MODEL_OK / router-unloaded-autoload) |

Stub routing (`tools/round100-props-status.py:102-115`): `/v1/models` → 200 fixture; any other
path → 404 empty body; `/props` → the per-cell answer. **S6's `Location: /elsewhere` therefore
points at a 404 stub, not at a 200.** That single fact explains blind spot #1 below.

Claim wording (plan line 75, counter docstring line 8):
*"the probe reads the router's bare `/props` body only on a final HTTP 200"*
(frozen probe implementation: `tools/kama-probe.sh:904` `[ "$pcode" = 200 ] || return 2`,
with curl run **without** `-L`, so `%{http_code}` is the *first* response's status).

## 2. Mutants, exactly ONE change each (gate = line 904 unless noted)

All mutants start from `git show 2e27e6f1:tools/kama-probe.sh` (sha256
`23b26d76…a685a74` — equals the committed receipt's `probe_sha256` in
`measured/c2.out:19`, confirming the frozen bytes).

| id | mutant file | ONE change to `router_autoload()` | Expected if counter is sound |
|---|---|---|---|
| unmodified | `probe-unmodified.sh` | none (oracle) | exit 0 |
| (a) any-2xx | `probe-a-any2xx.sh` | gate → `case "$pcode" in 2??) ;; *) return 2 ;; esac` | exit 1 via S5-202 |
| (b) <400 | `probe-b-lt400.sh` | gate → `case "$pcode" in 3??\|4??\|5??) return 2 ;; esac` | exit 1 via S5-202 |
| (c) follow `-L` | `probe-c-followL.sh` | add `-L` to curl flags (`--max-filesize … -L -o …`), gate unchanged | exit 1 via S6 *if* -L changed the verdict — see finding |
| (d) ignore-if-router | `probe-d-ignore-if-router.sh` | fall through to body-parse on non-200 when body is a router doc | exit 1 via S1–S6 |
| (e) not-500 | `probe-e-not500.sh` | gate → `[ "$pcode" != 500 ] \|\| return 2` | exit 1 via S1,S3–S6 |
| (f) dropped (= base) | `probe-f-dropped.sh` | gate removed (`true # status gate dropped`) | exit 1, 6 mismatches (reproduces `c2-base.out`) |
| (g) 000-as-200 | `probe-g-000-as-200.sh` | gate → `[ "$pcode" = 200 ] \|\| [ "$pcode" = 000 ] \|\| return 2` | **BLIND SPOT — see §4** |
| (h) 200-or-304 | `probe-h-200or304.sh` | gate → `… \|\| [ "$pcode" = 304 ] …` | **BLIND SPOT — see §4** |
| (i) 200-or-204 | `probe-i-200or204.sh` | gate → `… \|\| [ "$pcode" = 204 ] …` | **BLIND SPOT — see §4** |
| (j) glob `2?*` | `probe-j-glob2x.sh` | gate → `case "$pcode" in 2?*) ;; *) return 2 ;; esac` | exit 1 via S5-202 |
| (k) numeric `-eq` | `probe-k-numeric.sh` | gate → `[ "$pcode" -eq 200 ] 2>/dev/null \|\| return 2` | exit 0 — wording-equivalent on stub codes (not a blind spot, §3) |
| (l) 200-or-302 | `probe-l-200or302.sh` | gate → `… \|\| [ "$pcode" = 302 ] …` | exit 1 via S6-302 |
| (m) blanket | `probe-m-blanket.sh` | gate → `return 2` (always unread) | exit 1 via P1,P2 (reproduces `c2-mutant-blanket.out`) |
| (n) leaky-on | `probe-n-leaky-on.sh` | gate dropped (`true`) — same shape as (f) | exit 1 (duplicate of (f); kept as independent-code-path check) |

## 3. Fresh runs (2026-11-08, this seat) — exit + summary line per mutant

Command for every row: the §0 public path with that row's `--probe-file`. Full receipts:
`.ufo/waves/round-100/w1/out/EX01PropsForge/probe-<id>.out.txt` (19 lines each: 18 CELL lines
+ summary + `exit=`).

| mutant | exit | ROUND summary (`mismatches`) | MISMATCH cells (verbatim wants) |
|---|---|---|---|
| unmodified | **0** | cells=9 mismatches=0 flips=6 stable=3 met=True | — |
| (a) any-2xx | 1 | mismatches=1 | `S5-202-router-on want=…/router-autoload-unread/2 got=MODEL_OK/…/0` |
| (b) <400 | 1 | mismatches=1 | `S5-202-router-on` (same as (a)) |
| (c) follow `-L` | **0** | mismatches=0 flips=6 stable=3 met=True | — |
| (d) ignore-if-router | 1 | mismatches=6 | S1,S2,S3,S4,S5,S6 |
| (e) not-500 | 1 | mismatches=5 | S1,S3,S4,S5,S6 (S2 passes: 500 excluded) |
| (f) dropped | 1 | mismatches=6 | S1–S6 — **byte-identical behaviour to committed `controls/c2-base.out`** |
| (g) 000-as-200 | **0** | mismatches=0 | — |
| (h) 200-or-304 | **0** | mismatches=0 | — |
| (i) 200-or-204 | **0** | mismatches=0 | — |
| (j) glob `2?*` | 1 | mismatches=1 | `S5-202-router-on` |
| (k) numeric `-eq` | **0** | mismatches=0 | — (see below) |
| (l) 200-or-302 | 1 | mismatches=1 | `S6-302-router-on` |
| (m) blanket | 1 | mismatches=2 | P1, P2 — **identical to committed `controls/c2-mutant-blanket.out`** |
| (n) leaky-on | 1 | mismatches=6 | S1–S6 (same as (f)) |

Cross-checks that passed: unmodified sha `23b26d76…` = `measured/c2.out` probe_sha256;
(f) reproduces `c2-base.out`'s 6 mismatches at the same cells; (m) reproduces
`c2-mutant-blanket.out`'s 2 mismatches (P1+P2 only). The harness therefore measures the
frozen bytes, not a drifted counter.

**About (k):** `[ "$pcode" -eq 200 ]` is exit 0 *and* wording-equivalent for every code curl
can emit here (3-digit decimal, no leading zeros). Leading-zero forms (`"0200"`), whitespace,
and rc-redirect cases are outside the stub alphabet; on the graded domain this mutant is
observationally identical to the frozen gate. **Not counted as a blind spot** — no cell could
distinguish it without inventing a code `%{http_code}` never prints.

## 4. BLIND SPOTS — wording violations that exit 0

Each of the following violates *"reads the body only on a final HTTP 200"* (plan line 75;
counter line 8) yet exits 0. For each: why it's green, the cell that would kill it.

### BS-1 — `-L` redirect-following is invisible (mutant (c), `probe-c-followL.sh`)

- **Violation:** with `-L`, `%{http_code}` is the status *after* redirects. A 302 whose
  `Location` returns 200 + router-shaped body would be read. The claim and the frozen probe
  state the opposite: `router_autoload()`'s header (lines 896–897): *"curl does not follow
  redirects here (no -L), so a 3xx is graded by its own status."*
- **Why it is green:** the stub's S6 Location is `/elsewhere`
  (`round100-props-status.py:26,79`), and the stub `Handler.do_GET` answers **every non-`/props`
  path with 404** (lines 111–113). With `-L`, curl follows /props→302→/elsewhere→**404**,
  `%{http_code}` is 404, the unchanged gate rejects it, result UNREAD = want. The receipt
  confirms all nine tip cells identical to the frozen tip (`probe-c-followL.out.txt` lines
  10–18). **No cell in the suite makes a redirect land on a 200.**
- **Killer cell (add):** S8-302-to-200: `/props` → 302 + `Location: /props-200`, plus a
  `/props-200` route serving 200 + `{"role":"router","models_autoload":true}`. Frozen want:
  UNREAD (no `-L`, body never read). With `-L` the body is read → `MODEL_OK/…/0` → mismatch.
  This is a stub-routing change, not a new verdict cell: it makes the `Location` target exist
  as a 200.
- **Severity:** medium. A proxy/intranet fronting a router that 302s to an authenticated URI
  is precisely the "proxy, a cache, a redirect page" the frozen comment promises to reject
  (line 895–896). Today the counter cannot tell `-L` from no-`-L`.

### BS-2 — transport code `000` accepted as 200 (mutant (g), `probe-g-000-as-200.sh`)

- **Violation:** `000` is curl's "no HTTP response" (connect refused, DNS failure, TLS error,
  timeout). Accepting it means reading whatever bytes sit in `"$pbody"` from a *previous*
  run — `pbody` is `$TMP_ROOT/props<port>.body` (probe line 900) and is not truncated before
  curl runs; on transport failure curl writes nothing and `%{http_code}` prints `000`.
  Reading a stale body under `000` is reading without a final HTTP 200.
- **Why it is green:** every cell is served by a live loopback stub; `{http_code}` is always a
  real 3-digit code, never `000`. No cell exercises a refused/timeout `/props` read.
- **Killer cell (add):** S9-unreachable: the probe pointed at a **closed loopback port**
  (bind-then-close or a port known closed), want UNREAD (router-autoload-unread), exit 2.
  A `000`-as-200 probe would fall through to the body parser over the stale/empty `pbody`
  (`json.load` fails → `unread` → UNREAD… only *accidentally* right). A harder variant kills
  the stale-read directly: pre-seed `props<port>.body` with a router-on document, then a more-robust
  killer is S9b-stale-body: close port + pre-seeded router-on body → frozen
  gate correctly rejects (`000≠200`) → UNREAD, while `000`-as-200 reads the seed →
  `MODEL_OK`. Either cell makes (g) red.
- **Severity:** high for a stale-read (false `MODEL_OK` on reconnect), low on any
  fresh-empty body (accidental UNREAD). The claim says *only* on a final HTTP 200; `000` is
  by definition the absence of a final HTTP status.

### BS-3 — 304 (and 204) silently admitted (mutants (h), (i); shape of the whole untested class)

- **Violation:** `200 or 304` and `200 or 204` both exit 0. A 304 body is empty by RFC; a 204
  body is empty by RFC; reading either is reading the body under a non-200 status. 204 is
  doubly nasty: *"203–205"* and other 2xx statuses are all in the same untested class — the
  suite tests exactly **one** non-200 2xx (202, S5).
- **Why they are green:** no cell serves 203–299 except 202, no cell serves 3xx except 302.
  On an empty body the fallback parser prints `unread` anyway
  (`router_autoload()` lines 906–921: `json.load` on `b""` → exception → `unread`), so even a
  gate that admits 304/204 yields UNREAD — the *verdict* is right for the wrong reason, and
  the counter cannot see the reason. Any cell that coupled a 304/204 status with a router-shaped
  body would be a lie about the wire, but a *conditional-request* cell (see below) catches
  the real deployment case.
- **Killer cells (add):** S10-304-cached and S11-204-cond: serve 204 + empty body drawn from
  a stale-seeded cache file, or serve 304 with a `Content-Length`-less empty body after a
  first 200 that populates `"…/props$port.body"` — i.e. seed the body file and admit via the
  mutant; frozen want UNREAD regardless. Concretely: reuse the BS-2 seeding technique —
  seed `props<port>.body` with router-on, stub returns 304/204 → mutant reads seed → `MODEL_OK`
  → mismatch. Without the seed, no 304/204 cell can ever be red (body-parse masks the gate),
  which is exactly the blind spot: the gate is the onlyбеж guard for empty-body statuses.
- **Severity:** medium as a class (ungraded statuses: 100–199, 203–299, 301, 303, 304, 307,
  308, 400, 404, 501, 505, …). The plan discloses this partially: *"other non-200 statuses
  follow the same `[ "$pcode" = 200 ]` line but are not each graded"* (plan lines 111–112).
  That disclosure explains why (h)/(i) are green on *this* counter, but it does not cure the
  wording/number mismatch: the header sentence (line 75) claims "only on a final HTTP 200",
  and three concrete mutants prove the counter would certify a probe that does otherwise.

## 5. Which cells do the work, and how narrow is the freeze?

- **S5-202-router-on** is the sole killer of (a) any-2xx, (b) <400, (j) glob `2?*`. All of
  those mutants fail on exactly that cell (receipts lines 19–20 each). One cell carries the
  whole "not just any 2xx" width.
- **S6-302-router-on** kills (l) 200-or-302 but — because its Location target 404s — does
  **not** kill (c) `-L`. The 302 "killer" cell is therefore weaker than it looks: it grades
  *no-redirect as a status*, not *no-following as a behaviour*. BS-1 is the sharpest instance
  of the Amendment-59 shape the packet describes (counter green on a property narrower than
  the wording): **only-when-the-final-status-is-200 is graded only for the statuses whose
  bodies the stubs happen to answer next.**
- **S1/S3-style off-under-error cells** grade reason-string difference
  (`router-unloaded` vs `router-autoload-unread`), which is what makes (d) and (e) red even
  when the verdict stays `MODEL_UNLOADED`. Without that reason check, (d)'s S1/S3 half would
  also pass. Good: the reason is load-bearing where it matters.
- **Base mutant (f) reproduces the committed defect exactly** — 6 mismatches at S1–S6, same
  verdicts as `controls/c2-base.out` — so the freeze-vs-base delta the claim stands on is real
  and this harness can resolve it.
- **Disclosed limit that partially covers (h)/(i):** plan lines 111–112 say other non-200
  statuses "are not each graded". I credit that disclosure for the *ungraded class*; but the
  claim's one-line header ("only on a final HTTP 200", plan line 75; counter phrase
  "only when the final HTTP status is exactly 200", counter line 8) and the probe header
  ("a 3xx is graded by its own status", probe line 897) each make a *behavioural* assertion
  the 9-cell suite does not prove. The gap between the disclosed "not each graded" and the
  asserted "only/exactly" is the falsifies-wording core (§7).

## 6. Notes, limits, and process

- **Own reported verdict is on C2 only.** I never opened C1's audit tooling beyond reading
  the plan/counter docstring surface; no C1 mutants were built, so no C1 evidence exists here.
- **Sibling writes:** `git status --porcelain` shows `M corpus/knowledge/probe-answer-bounds.md`
  and `M corpus/knowledge/router-mode-readiness.md` (17 ins, 2026-11-08 20:15). These are
  **not** my writes — mv timestamps predate my battery and I never directed a write there. I
  treat them as sibling-lane edits and did not read, revert, or amend them.
- **Runner persistence:** `run_mutants.py` was written into my out dir by `write` (tooling
  policy satisfied: scratch → copy receipts into out dir first, then scratch cleanup). The
  battery ran ~157 s wall (15 mutants × base+tip × 9 cells); loopback stubs only, ephemeral
  ports, no operator router contacted. No `git add/commit`; scratch
  `/fast/scratch/hyaku/kama-r100/EX01PropsForge/` held `probe-m.sh` + `run.log` + per-mutant
  `work-*` dirs and was removed before yield (see §8).
- **What I did not do:** no `pip/uv/cargo` installs (no need), no tunnelling/redirect proxy
  beyond the mutant's `-L`, no 204/304 wire-lie cells beyond the analysis in BS-3 (building
  them would be editing the frozen counter, forbidden by the packet). The proof that (c),(g),
  (h),(i) are green uses the counter exactly as frozen.

## 7. Verdict rationale (the pre-file gate's three-way)

The defect class to hunt: *a frozen counter green on a property narrower than the claim*
Amendment-59. Three concrete mutants prove it for C2:

- (c) `-L` is green (**verdict `falsifies-wording`**): the claim's wording ("only on a final
  HTTP 200", and the probe header's "curl does not follow redirects (no -L)") is a behavioural
  assertion; the only 302 cell's Location resolves to 404, so follow-vs-not-follow is
  observationally identical on the graded domain. Killer = S8-302-to-200 (or equivalently
  point S6's Location at a 200).
- (g) `000`-as-200 is green (**`falsifies-wording`**): `000` is the absence of a final HTTP
  status. The suite never serves a transport-failure cell, so the exact property "only when a
  final status exists and is 200" is ungraded. Killer = closed-port cell (S9/S9b with a
  pre-seeded body).
- (h)/(i) 304/204-admission is green (**`falsifies-wording`**): graded 2xx = {200, 202} only;
  any other non-200 code slips through with an empty-body parser masking the gate. Killer =
  seeded-body 204/304 cells. Partially disclosed ("other non-200 statuses … not each graded",
  plan lines 111–112) — the disclosure and the "only/exactly" header sentence cannot both be
  true of the graded surface.

A fourth green mutant, (k) numeric `-eq 200`, is **not** a counterexample (observationally
identical on curl's alphabet) and is not claimed as evidence.

For C1: not attacked by this seat — `neutral` strictly on the basis that no evidence was
gathered, not that the claim was verified.

## 8. Receipts index (all under `kama-shokunin/`)

| file | what |
|---|---|
| `.ufo/waves/round-100/w1/out/EX01PropsForge/run_mutants.py` | mutant maker + runner |
| `.ufo/waves/round-100/w1/out/EX01PropsForge/probe-<id>.sh` ×15 | the mutants, one change each |
| `.ufo/waves/round-100/w1/out/EX01PropsForge/probe-<id>.out.txt` ×15 | counter receipt per mutant |
| `.ufo/waves/round-100/w1/EX01PropsForge.md` | this report |

Scratch `/fast/scratch/hyaku/kama-r100/EX01PropsForge/` — removed before yield (no residue;
no `/tmp` writes >50 MB; no lane index touched).

## Verdicts

VERDICT C2 falsifies-wording C2-3 green wording violators: -L unseen (S6 Location 404s), 000-as-200 ungraded (no transport-failure cell), 304/204-admitted masked by empty-body parser; counter green on narrower property than 'only on a final HTTP 200' (plans/round-100-claims.md:75; tools/kama-probe.sh:896-897 no -L promise), killer cells S8/S9/S10
VERDICT C1 neutral Not attacked by this seat; no C1 mutants or evidence gathered.
