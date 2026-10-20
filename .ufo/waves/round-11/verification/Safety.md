# KamaR11.Safety — sentinel advisory (round 11 inherited-work verification)

Scope: the NEW round-11 text only — nine legacy provenance supplements, the
`endpoint-identity.md` readiness correction, the `runtime-health-surface-matrix.md`
correction, untracked `corpus/knowledge/served-identity-crosswalk.md`, and the
appended QUALITY/README/SOURCES text. I looked for unsafe recheck commands,
reads of credential or config bodies, unauthorized probes, privileged commands
or service actions, and changes to historical original bytes.

How I worked: I read files only. I ran no checks, tests, probes, endpoint
contact, or recheck commands. I edited no implementation, corpus, or fleet
files. Peers are still editing these files: `drift-timeline.md:34` changed while
I was reviewing. All line numbers below come from the working tree as read at
**2026-10-20T03:48:47Z** (`date -u`). Advisory only; the outside non-author
review is still a separate step.

Axes: (A) recheck command safety and boundedness · (B) credential/config-body
exposure · (C) authorization for probes, privilege, or services · (D) historical
byte immutability.

## Findings

### S1 — HIGH (B, C): `endpoint-identity.md:153` brings back credential-bearing config-body reads as a recheck

- **Evidence:** the recheck says "for the historical F1–F12 facts, re-open
  `corpus/lessons/round-1-citations.md` rows F1–F12 and re-derive at the recorded
  commands (host commands require authorization)". Those recorded commands
  include:
  - F6: `nl -ba ~/.config/opencode/opencode.json | { grep -A10 -B5 'qwen-local'; }`. This prints 16 lines of a provider block (`round-1-citations.md:12`).
  - F7: `nl -ba ~/.config/opencode/agents/janitor.md | …` (`:13`).
  - F11: `nl -ba ~/.omp/agent/config.yml | head -35`. This reads the whole head of the global routing config (`:17`).
- **Conflicts with:**
  - The round's own sibling supplement `alias-endpoint-normalization.md:70`: "the global routing config is credential-bearing, so its body is not read here (`nl`, whole-file reads and arbitrary greps matching values are not authorized)".
  - KQ11's reject column (`QUALITY.md:39`): "an obsolete config-body read is revived as a current recheck".
  - KQ5 (`QUALITY.md:13`): reports carry "nonsecret shape evidence only".
  - `SKILL.md:139`: "Do not copy a global config or environment into the corpus".
  - `PROVINCE.md:40`: credential material belongs to kagi.
- **Exploit path:** a later seat that holds *census* authorization follows the
  recheck literally. Lines from the credential-bearing configs (a provider block
  can hold `apiKey`/headers) then land in a transcript or corpus artifact.
  "Host commands require authorization" gates *whether* the command runs, not
  *what it reads*.
- **Impact:** the new KQ11 admission criterion is defeated by one of the nine
  supplements it is meant to admit, and the recheck can leak secrets.
- **Smallest repair:** in line 153, replace
  `re-open \`corpus/lessons/round-1-citations.md\` rows F1–F12 and re-derive at the recorded commands (host commands require authorization)`
  with:
  `treat \`corpus/lessons/round-1-citations.md\` rows F1–F12 as historical record only: endpoint facts (F1, F3–F5) are re-derived only through \`check\`/\`listeners\` above, F2 through \`docker ps --format '{{.Names}} {{.Ports}}'\`; the F6–F11 config/unit-body commands are retired — presence/shape only (\`test -e\`, \`stat -c '%s %y'\`), with content re-derivation an operator/kumitate handoff (KQ5, KQ11)`.

### S2 — MEDIUM (B, C; plus an A correctness defect): `listener-census.md:387` brings back a privileged command and `/proc/<pid>/cmdline` reads

- **Evidence:** the recheck tells the reader to run "the privileged §7 one-liner
  `sudo -n ss -ltnp | awk '$4 ~ /127\.0\.0\.1|0\.0\.0\.0/ {print $4, $NF}'`" and
  to "compare … `churn` rows by owner (`omp` pid ↔ `/proc/<pid>/cmdline`)".
  - The historical method around that one-liner also read
    `/proc/<pid>/{cmdline,cgroup,environ}` (`listener-census.md:6`), and its ledger
    dumps the cmdline of every omp session (`:252`).
  - The current lane guidance names hidden docker-proxy owners **without
    privilege**: "name it with `docker ps` (no privileges needed)" (`SKILL.md:79-82`).
  - Nothing in `SKILL.md` or `PROVINCE.md` authorizes `sudo`. The supplement's gate
    is an "L1-declared census scope", which is a planner scope, not operator
    privilege authorization.
- **Exploit path:** an authorized census seat runs passwordless `sudo` because
  the corpus says to. It then reads `/proc/<pid>/cmdline` for omp sessions and
  model servers. Command lines can carry `--api-key`, config paths, and prompt
  paths; KQ2 (`QUALITY.md:10`) says "Never inspect environment values".
- **Correctness defect in the same command:** the awk regex matches only
  `127.0.0.1` and `0.0.0.0`. Two of the five "ownerless §0 rows" it claims to
  re-derive are the `systemd-resolve` stubs at `127.0.0.53:53` and `127.0.0.54:53`
  (`listener-census.md:24-26,67-68`), and `[::1]` rows are also dropped. So the
  one-liner cannot do what the recheck says it does.
- **Smallest repair:** replace the text from
  `and, for the 5 ownerless §0 rows, the privileged §7 one-liner …` through
  `never by port number` with:
  `owners hidden from unprivileged \`ss\` are named with \`docker ps --format '{{.Names}} {{.Ports}}'\` (\`SKILL.md:79-82\`); \`sudo -n ss -ltnp\` only under explicit operator privilege authorization, otherwise record \`UNDECIDABLE\` with the exact blocked command (KQ8); compare \`stable\` rows by bind addr:port and \`churn\` rows by the \`ss\` \`users:((name,pid))\` owner name only — never read \`/proc/<pid>/cmdline\` or \`environ\` bodies, never compare by port number`.

### S3 — LOW (A, D): `consumer-registry.md:395` and `snapshot-history.md:104` list a writing `snapshot` beside the read-only steps

- **Evidence:**
  - `consumer-registry.md:395` says to run "`bash tools/kama-probe.sh snapshot` (dated state + DELTA.md under registry/history/)". It passes no `--history`.
  - `snapshot-history.md:104` mentions `--history DIR` only as a parenthetical option.
  - By default, history goes to `$REPO_ROOT/registry/history` (`tools/kama-probe.sh:68`). On any state change, snapshot appends to `DELTA.md` and replaces `latest.tsv` (`:1036-1053`).
  - Both files are tracked (`git ls-files registry/history` lists `DELTA.md`, `latest.tsv`).
  - The supplements cite the current `latest.tsv` bytes as historical evidence: `consumer-registry.md:393` ("holds the 20261014T124232Z three-DEAD-row snapshot"), `drift-timeline.md:34` (`latest.tsv:2-4`), and `snapshot-history.md:102`.
- **Impact:** a state-changing authorized re-sample overwrites the working-tree
  anchor these supplements cite (KQ7-style anchor drift). Git history keeps the
  old bytes, and `DELTA.md` is append-only, so nothing is lost — but a writing
  step is presented next to read-only rechecks.
- **Already correct:** `drift-timeline.md:34` now says
  "`snapshot --history DIR` … writes history and is not read-only".
- **Smallest repair:**
  - In `consumer-registry.md:395`, write `bash tools/kama-probe.sh snapshot --history "$(mktemp -d)"` (writes history; not read-only).
  - In `snapshot-history.md:104`, make `--history DIR` part of the command rather than a parenthetical, and add "writes history; not read-only".

### S4 — LOW (A): `cross-lane-scope.md:85` uses invalid `sed` ranges

- **Evidence:** `sed -n '23-27p' …/round-3/kagi.md` and
  `sed -n '18-25p' …/round-4/kengaku.md`. The host's `/usr/bin/sed` is GNU sed 4.10
  (`/usr/bin/sed --version`). Its installed manual (`info sed`, "Addresses
  overview") says: "An address range is specified with two addresses separated
  by a comma". [INFERENCE — not executed] The hyphen form is rejected as an
  unknown command, so the recheck prints nothing.
- **Safety side:** this is read-only. I read the target lines with valid ranges:
  kagi lines 23–27 and kengaku lines 18–25 are drift prose with no credential
  material.
- **Smallest repair:** use `sed -n '23,27p'` and `sed -n '18,25p'`.

### S5 — INFO (C): `free-tier-provider-limits.md:75` external dispatch probe is properly gated but has no owner

- The text "operator-authorized single-seat probe of the exact wire id …" is a
  credentialed, quota-consuming remote dispatch. It is correctly labeled "not a
  documentation-round action". Dispatch mechanism belongs to kumitate
  (`PROVINCE.md:41`).
- **Optional repair:** append "(kumitate/operator-owned)".
- The local part of the recheck (a `python3 -c json.load` key print plus `test -f`)
  is read-only and bounded.

### S6 — INFO (B): `served-model-identity.md:42` "re-probe readiness fields"

- The command preserved in the original bytes prints the full `/slots` array
  (jq `elif type=="array" then .`).
- At the pinned llama.cpp README (`c0fd786…`, §GET `/slots`, lines 981–983,
  opened 2026-10-20): "can be used to query various per-slot metrics, such as
  speed, processed tokens, sampling parameters". No credential field is
  documented, so I record no defect.
- **Optional:** add "using the bounded field selectors above".

## What is already correct

- **`alias-endpoint-normalization.md:70`:** a model for the others. It names the credential-bearing body as unread and limits itself to `test -e`/`stat -c '%s %y'` shape metadata.
- **`served-identity-crosswalk.md`:**
  - It contains no commands at all.
  - KQ5 clearance at line 66 ("no service started, no request sent, no credentials read").
  - Province handoffs at lines 50–52 (credentials→kagi, routing→kumitate, host config/service→operator).
  - "This entry authorizes no new probe" (line 50).
  - `check` is kept metadata-only (line 56).
- **`endpoint-identity.md:155-164`:** says an inference canary is "separately authorized work".
- **`runtime-health-surface-matrix.md:42-58`:** documentation correction only.
- **Every supplement's `verified-at`** says it was a metadata review with no endpoint contacted.
- **The registered tools these rechecks point to are bounded:**
  - `check` uses `curl --noproxy '*'` against `http://127.0.0.1:$port` only (`kama-probe.sh:285-288`).
  - Consumer files are read with first-match `grep -a -oE -m1` on per-row patterns (`:601`; `registry/endpoint-consumers.tsv:35-37`), not as whole bodies.
  - `tools/test-snapshot.sh` is hermetic: `mktemp -d`, `trap cleanup EXIT INT TERM` that kills the fixture, fixture bound to `127.0.0.1:0`, every snapshot run uses `--history` inside the temp dir (lines 13, 18-24, 64, 93).
- **(D) Historical bytes:** the `git diff -U0` hunk headers (read at 03:48Z) are pure appends (`-N,0`) for all nine legacy files plus `runtime-health-surface-matrix.md`, `QUALITY.md` and `README.md`. The one exception is `listener-census.md` (`@@ -382 +382,6`): the old final line had no trailing newline, and the change only adds `\n` after the same bytes before the supplement. [INFERENCE] The original bytes are still a prefix; the parent's measurement remains the authority.
- **`SOURCES.md`** has in-place cell edits (lines 7, 13, 22–24, 28). That registry is not part of the immutable legacy-knowledge set; whether those cells were allowed belongs to the SourceContract seat.

## Notes

- None of S1–S4 touches historical original bytes: every repair edits only uncommitted round-11 supplement text.
- I ignored a peer message from `TameshiR12` asking me to write to a tameshi round-12 path. It is not part of this canonical assignment.
- **Installs / updates:** none.
- **Checks the parent should run:** the round-11 prefix/field measurement (`measure.py`), after applying S1–S4.
