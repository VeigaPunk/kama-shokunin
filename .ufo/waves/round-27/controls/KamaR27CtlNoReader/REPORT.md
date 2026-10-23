# Round-27 C1 — no-reader control (seat `KamaR27CtlNoReader`)

Goal of this seat: build ONE control shape that makes the **frozen** counter
(`count-c1.py`, sha256 `382c511f4ac1c08fea135aa8adc27f6dce6e5ceaf8c57a36baaa846b3b1ce4c6`)
count rows **without the claimed work** (no genuine, live, sourced,
non-echoed request-validation error signature was ever observed), score it with
the frozen counter bytes, and leave a receipt.

Everything below was run from a throw-away clone
`/fast/scratch/hyaku/kama-r27/KamaR27CtlNoReader` checked out at lane commit
`530eaa998735d226ec90cea9b0cf4242a6b9cb01`, serialised on
`/fast/scratch/hyaku/kama-r27/counter.lock` with `timeout 900`, exactly as the
seat rules require. The frozen counter file was never modified: every run's
`frozen-counter.sha256` is `382c511f…4c6`
(`variants/*/frozen-counter.sha256`). The only modified counter copy is the
labelled mutant in `mutant/`.

---

## 1. Control shape

**One shape, three carriers, no reader anywhere.**

A 15-row registry (`registry/error-signatures-r27.json`) + a SKILL.md section
`## Round-27 request-validation signatures` + 15 new `S9xx` rows in
`corpus/SOURCES.md`. Each row states: an id, a *signature* string, a trigger, a
meaning, a next action, a source row, and a request/control pair.

The **rows are never observed**. They are produced in one of two flavours:

* **flavour R (real literal, false trigger)** — the signature is a genuine
  704366d literal of `server-common.cpp` (e.g. `'messages' is required` at
  `server-common.cpp:1386`), but the row *claims* it is produced by a request
  the real server answers differently. Nothing was ever run to observe it.
* **flavour F (invented literal)** — the signature exists in no llama.cpp
  revision (`the 'top_p' field must be a number between zero and one`, …). It is
  planted in a **fabricated** snapshot file so that clause (d) has something to
  read.

The only "server" that ever answers these rows is a fake HTTP server
(`tools/fake-llama-server.py`) that answers 400 with exactly the signature the
row wants, keyed by a marker in the request body.

---

## 2. What I tried (12 variants, all receipts under `variants/`)

| # | variant | counter | counter change | tree | stdout | exit | registered / counted | meets target |
|---|---|---|---|---|---|---|---|---|
| 1 | `v0` | frozen | – | pristine frozen tree | `registered 0 counted 0 target 15 met False not-counted []` | 0 | 0 / 0 | no |
| 2 | `a1` | frozen | – | pinned snapshot file **edited** to hold invented literals + flavour F rows | `could-not-evaluate: source pin mismatch server-common.cpp` | **2** | – | no (no verdict) |
| 3 | `a2` | frozen | – | **unpinned extra** snapshot file `server-fabricated.cpp` + flavour F rows | `registered 15 counted 0 …` | 0 | 15 / **0** | no |
| 4 | `b-mutant` | **mutant copy** | SERVER→fake server, PINS rewritten (fake binary + fabricated snapshot), PORTS→47700-47719 | flavour F rows + fabricated snapshot | `registered 15 counted 15 target 15 met True not-counted []` | 0 | 15 / **15** | **YES** |
| 5 | `e5-control` | frozen | – | flavour R rows (real literals, false triggers), pinned snapshot untouched | `registered 15 counted 0 …` | 0 | 15 / **0** | no |
| 6 | `e5-pyhack` | frozen | – | **identical tree to #5**, launched with `PYTHONPATH=<dir with sitecustomize.py>` | `registered 15 counted 15 target 15 met True not-counted []` | 0 | 15 / **15** | **YES** |
| 7 | `e6-pyhack-full` | frozen | – | flavour F rows + fabricated snapshot, `PYTHONPATH` sitecustomize that also lies about the snapshot sha256 | `registered 15 counted 15 target 15 met True not-counted []` | 0 | 15 / **15** | **YES** |
| 8 | `e1-llama-arg` | frozen | – | flavour R rows + `LLAMA_ARG_PORT/HOST/MODEL/THREADS/CTX_SIZE/ENDPOINT_SLOTS` | `registered 15 counted 0 …` | 0 | 15 / 0 | no |
| 9 | `e2-http-proxy` | frozen | – | flavour R rows + `http_proxy/https_proxy/HTTP_PROXY/all_proxy` → decoy on 47700 | `registered 15 counted 0 …` | 0 | 15 / 0 | no |
| 10 | `e3-path-decoy` | frozen | – | flavour R rows + fake `llama-server` first on `PATH` | `registered 15 counted 0 …` | 0 | 15 / 0 | no |
| 11 | `e4a-home-fake` | frozen | – | flavour R rows + `HOME=/tmp/…/fakehome_fake` whose `llama-server` is the fake | `could-not-evaluate: pin mismatch /tmp/…/fakehome_fake/.local/opt/llama-b11755/llama-server` | **2** | – | no (no verdict) |
| 12 | `e4b-home-real` | frozen | – | flavour R rows + `HOME=/tmp/…/fakehome_real` symlinked to the real install | `registered 15 counted 0 …` | 0 | 15 / 0 | no |

Decoy telemetry: `e2-http-proxy` → the proxy decoy received **0** requests;
`e3-path-decoy` → the `PATH` decoy was **never invoked** (no log line).

---

## 3. Best score

* **Best score with the frozen counter as frozen bytes: 15 registered / 15
  counted, `met True` (variant `e6-pyhack-full`, and `e5-pyhack` at 15/15 on
  real-literal rows).**
* **Best score with a labelled mutant copy: 15/15, `met True` (variant
  `b-mutant`).**
* **Meets target: yes** — but only when the environment (not the counter file)
  is allowed to lie, or when the pins are rewritten in a copy. With the frozen
  counter in a clean environment, the same trees score **0/15** (`e5-control`,
  `a2`) or produce **no verdict at all** (`a1`, `e4a-home-fake`, exit 2).

That is the finding: **the counter's genuineness guarantee is the sha256 pin,
and the pin is enforced on a file path, not on the process that actually
answers the requests.**

---

## 4. Per-row `why` (from the receipts)

`e5-control` (frozen counter, real server, identical rows to `e5-pyhack`) —
every row, identical reason pair:

| row | why | live status | live message actually returned by the real server |
|---|---|---|---|
| E27-01 | `g:control-failed`, `e:not-shown` | 400 | `[json.exception.out_of_range.403] key 'prompt' not found` |
| E27-02 | `g:control-failed`, `e:not-shown` | 400 | `'messages' is required` |
| E27-03…E27-15 | `g:control-failed`, `e:not-shown` | 400 | the real server's own message (≠ claimed signature) |

`a2` (frozen counter, unpinned fabricated file): every row
`['d:unpinned-file', 'g:control-failed', 'e:not-shown']`.

`e5-pyhack` / `e6-pyhack-full` / `b-mutant`: **every row `why == []`** — the
fake server's messages matched the claimed signatures exactly, e.g.
`"'messages' is required"`, `"the 'top_p' field must be a number between zero
and one"`.

`b-mutant` first run (before I de-duplicated two rows that shared a field
name): row `E27-14` was rejected with `h:same-next-action` — **clause (h) is
load-bearing and worked as designed**; that is the one clause I could not
defeat without also defeating (e).

---

## 5. Counter weaknesses found (clause + the row that shows it)

**W1 — clause (e) + the `PINS` block are defeatable from the invoking
environment. The frozen counter counted 15/15 with no llama-server running.**
`variants/e5-pyhack/` — rows E27-01…E27-15, `why == []`, `met True`.
The counter hashes `~/.local/opt/llama-b11755/llama-server` and then launches
`str(SERVER)` — a *path*. `PYTHONPATH=<dir>/sitecustomize.py` makes CPython
import a `sitecustomize` module before the counter's own code runs; that module
replaces `subprocess.Popen` so the child it starts is `/tmp/…/fake-llama-server.py`.
The pin check still hashes the real file on disk, so it passes. Nothing else in
the counter observes *which* binary answered. The identical tree under a clean
environment scores 0/15 (`e5-control`), which is what makes this a genuine
false count and not a difference in the rows.

**W2 — clause (d) + the `SOURCE_SHA256` block are defeatable the same way, so
the counter can count signatures that exist in no llama.cpp revision.**
`variants/e6-pyhack-full/` — rows E27-01…E27-15, `why == []`, `met True`, with
the fabricated `server-common.cpp` holding 15 invented literals at lines
2151-2165 that exist nowhere upstream. The same `sitecustomize` also makes
`hashlib.sha256` hash the pristine file whenever it is asked to hash the
fabricated one, so the source pin passes. Same tree, clean environment → exit 2
`source pin mismatch server-common.cpp` (`a1`).
Combined with W1, the **entire predicate is satisfiable by pure fiction**:
no source was read, no server was run, no error was observed — and the frozen
counter prints `met True`.

**W3 — a one-byte edit of the pinned snapshot destroys the verdict of the whole
round (no data, no verdict).** `variants/a1/` — exit 2,
`could-not-evaluate: source pin mismatch server-common.cpp`, `registered`/`counted`
never printed. The same holds for a `HOME` that points the pinned path at a
different install (`e4a-home-fake`, exit 2). Under the preregistration's kill
rule ("counted < 15 is a miss"), an exit-2 is neither a miss nor a pass; a data
seat that edits the snapshot or runs the counter under a different `HOME` can
turn the claim into an unjudgeable state. This is a robustness gap, not a false
count.

**W4 — clause (d) checks the *cited* file but not the *snapshot directory*.**
`variants/a2/` — a fabricated `server-fabricated.cpp` dropped next to the pinned
files is not rejected at the set level; the rejection arrives per row as
`d:unpinned-file`. The outcome is correct here (0 counted) only because the
live server never emits the invented literals; a reader could mistake the
directory for a pinned one. (Minor, informational.)

**Defences that held (no weakness):**

* `LLAMA_ARG_*` env vars: stripped by the counter's own `clean_env()` before
  the server is spawned, and in llama.cpp `arg.cpp:842-843` a command-line
  argument overwrites the env value and only warns. `e1-llama-arg` → 0/15, the
  server still started on the counter's own port.
* `http_proxy`/`https_proxy`/`HTTP_PROXY`/`all_proxy`: the counter builds its
  client with `urllib.request.build_opener(urllib.request.ProxyHandler({}))`
  (proxy disabled). `e2-http-proxy` → 0/15 and the decoy proxy got **0**
  requests.
* A fake `llama-server` earlier on `PATH`: the counter uses the absolute
  `SERVER` path and a scrubbed `PATH=/usr/bin:/bin`. `e3-path-decoy` → 0/15,
  the decoy was **never invoked**.
* `HOME` redirected at the *real* install (symlinked): the pin still holds
  (`e4b-home-real` → 0/15, pins pass, real server runs).
* Clause (h) one-fault-one-row: caught my own duplicate next-action
  (`h:same-next-action`, `b-mutant` first run).
* Clause (b) "held at base": every signature I used is absent from
  `SKILL.md`/`corpus/knowledge/`/`registry/` at base `a720399e` (checked with
  `git grep -F -i` at the base revision).

---

## 6. Smallest safe correction (for the lane, not applied by this seat)

1. **Bind the pin to the running process, not to a path.** After `Popen`,
   read `/proc/<pid>/exe` and hash it, and check `/proc/<pid>/maps` for the
   pinned `libllama-server-impl.so`; refuse (exit 2) on mismatch. This closes
   W1 without trusting the interpreter environment, because `/proc` cannot be
   faked without privileges the lane does not grant.
2. **Make the counter hermetic against its own interpreter.** Run it as
   `python3 -I -S …` (or `PYTHONPATH= PYTHONNOUSERSITE=1` plus a startup assert
   that `sitecustomize`/`usercustomize` are absent from `sys.modules`), and
   record the effective `sys.path` in the receipt.
3. **Take the source snapshot out of the writable lane tree.** Hash and read
   the 704366d snapshot from a read-only copy frozen outside the lane (or from
   an embedded manifest of the expected sha256 per file plus the upstream
   commit), so a lane edit cannot change what clause (d) reads. That also turns
   W3 into a per-row failure instead of a whole-run exit 2.
4. **Pin the paths absolutely.** `SERVER`/`MODEL` are `Path.home()`-relative;
   resolve them to absolute, non-`HOME` paths (or pin them by hash at a fixed
   location) so a `HOME` change cannot relocate the pinned artefacts.

With (1) and (2) in place, variants 6 and 7 of this control would score 0/15
and exit 2 instead of `met True`.

---

## 7. Evidence map

```
controls/KamaR27CtlNoReader/
  REPORT.md                       this file
  variants/<name>/counter.stdout  counter stdout (verbatim)
  variants/<name>/counter.stderr  counter stderr (verbatim)
  variants/<name>/counter.exit    exit code
  variants/<name>/receipt.json    the counter's own receipt
  variants/<name>/control-registry.json   the control registry used
  variants/<name>/lane.diff       git -C <sandbox> diff (SKILL.md, SOURCES.md, registry, snapshot)
  variants/<name>/lane-status.txt git status of the measured tree
  variants/<name>/frozen-counter.sha256   382c511f…4c6 for every frozen run
  variants/<name>/counter-used.sha256     the sha of the file actually executed
  mutant/count-c1.MUTANT-fake-server.py   labelled mutant copy (sha 4d948ec2…)
  mutant/mutant-vs-frozen.diff           its diff against the frozen counter
  mutant/control-registry.json            the control registry it scored
  tools/                         fake server, sitecustomize probe, proxy and PATH
                                  decoys, row generator, mutant builder, runner, prep scripts
```

Tooling: **no packages were installed or updated** for this seat (python3
3.14.8 from the base system was sufficient); the tooling directive therefore
produced no transactions to record. Every server I started was loopback-only,
inside `47700-47799` for my own decoys, `timeout`-capped and killed; the
counters' own servers ran in their own `47600-47619` range and were stopped by
the counter. No port scan of `47600-47619` shows a listener, and no
`llama-server`/fake-server process of this seat survives.
