#!/usr/bin/env python3
"""Probe: does the frozen C2 counter's `superseded` class enforce the preregistration
predicate's word "live" (a base citation that RESOLVED at the frozen base)?

The preregistration predicate (round-55/preregistration.json, claims.C2.predicate) says:
  "`superseded` rows disclosing a live base citation re-pointed to a cited, resolving
   replacement"
The counter's own class comment (tools/round54-cited-path-check.py) says:
  "The token is no longer cited at tip, it WAS cited at base (unlike `fixed`, whose
   token was unresolved at base), and the replacement token is cited in that surface at
   tip and resolves."

check_row() is called with base_unres (the base's UNRESOLVED citation set). The
`fixed` branch consults base_unres ("fixed token was not an unresolved citation of this
surface at base"). The `superseded` branch does not consult base_unres at all - it only
checks base_citelines (the set of tokens CITED at base, resolved or not).

This harness calls the FROZEN check_row() with synthetic arguments (no lane tree is
mutated, no file is edited) to see whether a superseded row whose token was cited at
base but NEVER RESOLVED at base is accepted.

Usage: probe_superseded_live.py <counter-path>
"""
import importlib.util
import sys

counter_path = sys.argv[1]
spec = importlib.util.spec_from_file_location("r54c2", counter_path)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SURF = "SCORECARD.md"
TOK = "tools/never-existed.py"        # cited at base, resolves nowhere at base
REP = "corpus/lessons/round-53-verifier-spotcheck.md"   # cited + resolving at tip

row = {"line": 99, "surface": SURF, "token": TOK, "class": "superseded", "evidence": REP}

# cited_tip: the token is gone at tip; the replacement is cited and resolves.
cited_tip = {SURF: {REP: [(REP, "ok")]}}
# base_citelines: the token WAS cited at base (this is the only base fact checked).
base_citelines = {SURF: {TOK: {18}}}
# base_unres: the base's unresolved set. The token is NOT in it -> it RESOLVED at base.
base_unres = {SURF: set()}

print("counter:", counter_path)
print("token:", TOK)
print("base_unres contains token:", TOK in base_unres[SURF], "(False -> the token RESOLVED at base)")
why = m.check_row(row, None, None, None, cited_tip, base_unres, base_citelines, {}, set())
print("check_row(...) ->", repr(why), "(None == the row is accepted as honest)")

# Control: the same row but the token DID NOT resolve at base (it is in base_unres),
# i.e. it was an unresolved citation at base -> that is a `fixed`/`never` situation.
base_unres2 = {SURF: {TOK}}
why2 = m.check_row(row, None, None, None, cited_tip, base_unres2, base_citelines, {}, set())
print("control (token unresolved at base) check_row(...) ->", repr(why2))

# Does the `fixed` branch enforce the opposite requirement?
row_fixed = dict(row, **{"class": "fixed", "evidence": REP})
why3 = m.check_row(row_fixed, None, None, None, cited_tip, base_unres, base_citelines, {}, set())
print("fixed branch with a RESOLVED-at-base token ->", repr(why3), "(None == accepted)")
