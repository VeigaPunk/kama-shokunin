# Proposed additions to tools/kama-live-replay.py docstring (line numbers from 5dacf2c7)

Not applied: the lane is read-only for this seat. Each block names the docstring line it
should follow or replace (AST line numbers of the committed file at 5dacf2c7; see
docstring.txt in this directory for the exact current text).

## A. JSON key list (after current line 38, inside the "Writes J:" paragraph)

Current list stops at `"inputs": {...}`. Observed extra top-level keys: own_server,
live_child, live_exit.

     "own_server" {memfd, member, sha256, seals, dev, inode}: the memfd this replay filled
     from the archive member; live_child {isolated, env_keys, pdeathsig}: the isolation the
     live child got; live_exit: the live child's exit status (null until it exits).

## B. --live default and the tree it needs (after current line 33)

Current: `kama-live-replay.py --receipt R --work DIR --out J [--live TOOL] [--timeout S]`

Add:

     --live defaults to <directory of this script>/kama-llamacpp-live.py. That tool is not
     self-contained: it also needs <its directory>/kama-probe.sh and <parent of its
     directory>/registry/endpoint-consumers.tsv. Run the replay from a checkout (or a
     `git archive` extraction) of the lane at the recorded revision, not from a lone copy
     of kama-live-replay.py; otherwise the live child exits 2 and the replay refuses with
     `no-rerun-receipt:exit=2:<child stderr>`, or (when the child starts but cannot set
     up) reports a long mismatch list and exits 1.

## C. Refusal vocabulary (after current line 40)

Current text states the exit-2 category only. Observed `refused` strings (free-form):
  no-rerun-receipt:exit=<n>:<child stderr>
  provenance-verified-<field>-differs
  member-digest-mismatch:want=<sha256>:got=<sha256>
and the docstring's own mismatch reasons server-exe:*/model-mapping:* are mismatch text,
not refusal text. Note that a receipt-level digest tamper is caught at the archive-member
or provenance-consistency check, before any memfd is filled, so the round-52
`memfd-digest-mismatch` (current line 68) was not what a fresh session observes for a
tampered receipt.

## D. Usage block (current lines 32-35)

Omits the witness options documented two paragraphs later (current lines 42-45). Add a
fourth usage line:

     kama-live-replay.py --receipt R --work DIR --out J [--witness-dir D --witness-timeout S]

## E. Two facts worth stating in one line each

  line 41  --timeout: state the default bound (it is not stated or shown by --help).
  line 36  --work: created if absent (nested paths too); the current text says only that
           downloads go into --work.
