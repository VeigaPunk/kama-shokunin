VERDICT: partial — KQ37's two refusals (decoded echo, shared frame) close the server-echo and generic-row channels but leave the other seven leg-rejection classes unguarded; the missing generalisation is full shortcut-shape control coverage before data.

# ConnectorShortcutClasses — X1 / KQ37 cross-lane shortcut classes

## Pattern statement

Every shortcut class in the leg list (mori QUALITY.md §98, "leg-rejection shapes") is the same
failure in different clothing: **a counter credits a row on a property that a program can
manufacture without doing the claimed work, because the counted predicate is a proxy for
the claimed knowledge and the shortcut manufactures the proxy.** The counter's check is a
necessary condition of the work, never the work itself; a shortcut that produces the proxy
reads MET. KQ37's two refusals harden the proxy against two specific manufacturing
channels (request-carried echo and one-frame-many-rows) but do not remove the
proxy-vs-work gap for the other channels, and its control-receipt clause is scoped to "each
echo class the counter names", not to every leg-rejection shape.

## Class-by-class table

Applied to an error-signature counter that credits a live server error signature. Columns:
"decoded echo" = KQ37 refusal 1 (signature occurs in request path / JSON-decoded keys or
values / either serialisation); "shared frame" = KQ37 refusal 2 (one row per message frame,
signature cut out).

| Class (leg list) | KQ37 decoded echo | KQ37 shared frame | Why |
|---|---|---|---|
| generic rows (one generic message cited by many rows) | no | yes | same frame repeated with different spliced literals → refusal 2 collapses to one row |
| copied observed column | no | no | copies a value, not a request echo or frame; caught only by recycled/newness + control |
| server echo (request carried into error text) | yes | (yes if one frame) | refusal 1 is exactly this channel (S136/S137) |
| label-keyed programs | no | no | derives output from names/ids/labels, not request content; KQ37 never inspects labels |
| skip-work / do-nothing | no | no | absence of work; KQ37 is a content check on messages, not a work check |
| content-free shortcuts (boilerplate prose) | no | no | KQ37 explicitly does not judge trigger/meaning/next-action prose ("not_counted_boundary") |
| post-data shortcuts | no | no | static refusals cannot prevent post-hoc construction or deletion |
| no-decision glossary rows | no | no | KQ37 has no decision/verdict-content clause (mori M1) |
| rows deleted after judgment | no | no | KQ37 has no post-data mutation/deletion clause |

Non-leg classes named in round-27 `controls_required` (echo-assembly, log-help-warning,
env-injection, object-store, recycled, all-false, junk, no-reader, do-nothing) are likewise
not caught by either refusal except echo-assembly partially (refusal 1 only when the
signature occurs verbatim in a decoded value; transformed assemblies — detokenised ids,
case/schema rewriting — escape, as the knowledge entry §"What this does not establish"
states).

## One proposed generalisation KQ37 most lacks

KQ37's last clause requires "a non-author shortcut-control receipt for each **echo class**
the counter names". The cross-lane pattern (mori Q98; round-26/34) shows that the
dangerous classes are mostly non-echo. Round 27's own C1 was withdrawn because no committed
non-author control receipt existed for any class (attempt-2 control wave died), and the
preregistration's `controls_required` already names 14 classes of which only 2
(echo-replay, echo-assembly) are echo classes. The single generalisation that would make
KQ37 the error-signature specialisation of the leg principle:

> **Extend KQ37's control-receipt clause from "each echo class the counter names" to
> "each leg-rejection shape in the Q98 list (generic rows / copied observed column; server
> echo; label- or id-keyed answers; skip-work or do-nothing; content-free output;
> no-decision content; rule changed or rows deleted after data), or a stated
> inapplicability with its reason" — i.e. one named non-author control receipt per shape
> before any data seat, not per echo class.**

Evidence:
- mori Q98 (QUALITY.md lines 715-721) already requires this full shape-to-control
  mapping for any measured claim; KQ37 is narrower and therefore inconsistent with the
  fleet's own admission bar.
- round-27 preregistration `controls_required` names 14 classes, only 2 echo; A3 notes no
  committed receipt for any (lesson §C1 withdrawn).
- round-34 M2: 16 controls discharging every shape still missed a label-keyed,
  harness-keyed shortcut (post-data probe `ef936fb4`), so full coverage is necessary but
  not sufficient — consistent with the knowledge entry's "necessary, not sufficient".
- round-26: the base-tree shortcut was one generic frame + request-supplied string;
  refusal 2 catches the frame but not the label-keyed or post-data variants.

This keeps KQ37's two refusals intact (no harm to the calibration axis they already
improve) and adds the control-coverage requirement that the other axes (depth,
adjacency) already demand via Q98.

## Sources / pointers
- kama: corpus/knowledge/echo-discriminating-counters.md; corpus/QUALITY.md KQ37;
  corpus/lessons/round-26-verifier-spotcheck.md:98-116; .ufo/waves/round-27/preregistration.json
  (controls_required); .ufo/waves/round-27/count-c1.py clauses (f)/(h).
- mori: corpus/QUALITY.md §98 (lines 713-731), §99 (lines 733-746); corpus/lessons/round-34.md M1/M2.
- kumitate: corpus/lessons/round-44.md (skip-work control met counter; CtlPostDataA).
- round-26 shortcut evidence: .ufo/waves/round-26/w2-falsify/out/CriticShortcutRows/.