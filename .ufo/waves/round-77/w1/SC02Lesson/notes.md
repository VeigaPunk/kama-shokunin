# SC02Lesson evidence notes

Axes: calibration, freshness. This seat is a scribe, not an executor or judge.

## Commands actually executed by this seat

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master && git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --format='%H %s' --diff-filter=A -- plans/round-77-claims.md`

Exit 0. Output:

```text
7d60e2ab58866a0366937d61c9712483be57b36e
7d60e2ab58866a0366937d61c9712483be57b36e round-77: freeze claims (C1 baseline receipts, C2 register cutoffs, C3 round-76 facts) with base receipts and the 13-seat wave spec
```

This is the observed branch tip at this read, not a claim about the later landing tip. No counter, gate, test, fixture, install, VCS write, or other runtime was invoked by this seat.

## Source access

Specialized `read` opened https://www.postgresql.org/docs/current/ddl-system-columns.html live on 2026-11-04. Reader returned PostgreSQL 18 §5.6 System Columns; xmin identifies the inserting transaction for a row version, and ctid changes on update or VACUUM FULL. This source was rejected as authority for Git register-admission policy. Flip: an assigned database-backed audit implementation and its own measured witness. Reader calls have tool outcomes, not shell exit codes; no process exit is fabricated.

SC01Knowledge independently reports a live curl exit 0 for https://git-scm.com/docs/git-log on 2026-11-04, reserving S549; its located quote is “Any combination of the filter characters (including none) can be used.” at retained HTML line 6737 under --diff-filter. Source admission remains attributable to that seat, not this seat's fetch.

## Historical failure witness

Receipt: /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-76/measured/after/append-exempt-selftest.out

Recorded command: `TMPDIR=<scratch> python3 tools/round76-append-exempt.py --selftest`; recorded process exit 0 at revision c2aa7fb2c02dd95a185b728d5863f9ae492ecef4. It contains `APPEND_EXEMPT_SELFTEST rotation-reintroduced PASS exit=1 expected=1`. This is the arm's defective-input exit 1, not a failing overall selftest. Source report EX03AppendExempt limits this historical arm to injected introduction/ancestry facts; it is not end-to-end Git delete/re-add discovery evidence.

## Frozen text tension observed by source reading

Plan lines 101–103 say each row is under its own introduction cutoff, while scope ruling lines 113–118 admits row-event ancestry to the audit revision and treats append-only growth as non-rotation. Current C2 evaluate reads working-tree registers and validates row commits against data['to']; introduction history comes from that audit revision. Preserve both formulations; the lesson cannot resolve or amend the frozen predicate.

## Boundaries

No SCORECARD.md, LOG.md, corpus/README.md, plan, product code, source registry, or peer report was edited. No scratch tree was created by this seat, hence none is left to remove. The plan was read in full before this item; QUALITY.md and both prior lessons were read for shape.

## Evidence updates received before filing

SC01Knowledge corrected its initial quote count: the quoted Git sentence has 11 whitespace-delimited words, not 13. S549 now exists at corpus/SOURCES.md:301, tier B. This seat also opened https://git-scm.com/docs/git-log live and located the quote in reader output (artifact://69675, reader lines 2837-2842; retained HTML anchor remains line 6737). SC01 reports the preappend mirror census failed with exit 2 for missing scratch shokunin.conf, followed by a later real census exit 0. The lesson records failed KQ124 order rather than presenting the later green as repair.

EX02Registers explicitly reports no current selftest or demonstration executed. EX03Selfrecord likewise reports authored, unexecuted C3. Thus neither current rotation rejection nor the C3 after-target is execution-certified by this seat.

SC03 reports D1/D3/D4/D6 corrections authored and its named derivations exit 0. This seat read after-postcutoff.out and after-logtally.out directly. Their exact command lines and process exits are retained in those receipts:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-postcutoff.out: Python command reads the sealed round-76 append receipt and git merge-base ancestry; exit 0; pre=31 post=6 total=37.
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/SC03Corrections/after-logtally.out: Python command reads the sealed gate-selftest receipt and git grep for historical pass18 evidence; exit 0; pass21 backed, pass18 search exit 1 with zero matches. It does not invoke the gate.

D2 record correction and D5 green capability admission remain explicitly unverified at the scribe cut; those files are outside this seat's scope.

## Self-evaluation

Accuracy 4: source evidence is distinguished from unexecuted current counters; final landed commit binding is not available at this cut.
Completeness 4: all requested lesson sections and D1-D6 dispositions are recorded; the new rotation arm's actual failure run is unavailable, and the historical injected witness is explicitly bounded.
Clarity 4: frozen wording conflicts and worktree/historical-input split are explicit, though the source/receipt distinction adds length.
Actionability 4: parent can run the existing current rotation detector and C3 counter; this seat cannot supply their missing execution evidence under its scribe role.
Conciseness 4: detailed provenance is retained in notes rather than invented outcome summaries. Overall 4.0.
Highest-impact improvements: bind final committed bytes and retain a real current rotation-reintroduced failure receipt; append D2 correction before C3 measurement. These are integration checks, not claims already exercised.
Self-check: a reader should agree that authorship and historical red evidence do not establish a current green claim.
