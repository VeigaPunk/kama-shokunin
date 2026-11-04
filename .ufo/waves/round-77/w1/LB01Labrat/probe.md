# CR02 audit fixture receipt

Axis: freshness (C2); operability and calibration are guard axes, not separately scored here.

Read the full frozen plan before constructing the fixture. Lane master and freeze introduction both resolved to `7d60e2ab58866a0366937d61c9712483be57b36e`; base is `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`.

One fixture: `/fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT` (deleted before report). Seven commits: initial declarations; appended source row; permitted status-only edit; outside-region deletion; inside-region deletion; SCORECARD head edit; mixed source status/head edit. The SOURCES A-row contract additionally declares an exempt head to exercise both counters on one event. All three declarations bound. Before each fixture git write, a `git -C <fixture> rev-parse --show-toplevel` assertion equalled the fixture path. No lane git mutation, counter, selftest or pre-report gate was run.

Fixture status row has eleven cells and changes only status (`mined` → `accepted` → `retired`). Region contract is `only=## Errata@NOTES.md:2`; head contracts use `exempt=## Head` and preserve section size. The sole expected audit exit 1 is the deliberately un-restored inside-Errata deletion; the driver completed normally (exit 0). No dead-seat execution or suppressed command failure occurred.

## Exact answers

- Yes, under the audit's mechanical A-row definition: `permitted == deleted` holds only if every deleted line is recognized as a permitted row edit. Pure status edit: deleted=1, graded=0, ungraded=0, permitted=1. The check compares immutable parsed cells, not whole-row byte identity.
- Yes. `file_regions` returns `(set(), ['## Errata'])`: empty exempt titles and the Errata prefix. Parent sections distinguish outside (`## Body`, graded=0, ungraded=1) from inside (`## Errata`, graded=1, ungraded=0). Do not reverse the tuple or treat empty exempt titles as absence of an only-region.
- Yes, on a mixed event: deleted=2, graded=0, ungraded=1, permitted=1, status=ungraded. This disproves treating any positive permitted count as sufficient. It does not break the frozen C2 condition: `permitted == deleted and graded == 0 and ungraded == 0` correctly excludes this event.

## Verbatim commands, exits, and output

The following is the captured output of the Python module-import fixture driver. `exit=1` refers to `audit.exit_code(data)`, not a subprocess failure. Git invocations are literal argument joins; fixture commit subjects are single arguments. Module execution target is the fixture, never the lane.

```text
$ bash -c S=/fast/scratch/hyaku/kama-r77/CR02AuditProbe; export TMPDIR="$S"; D=$(mktemp -d -p "$S") && git -C "$D" init -q && printf "%s\n" "$D"
exit=0
/fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse --show-toplevel
exit=0
/fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m initial
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
b5daa0e94a1746c856ac5bd2a9771918014261e9

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m append source row
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
0c3e07931856099179e39ba86d971f59bb6f3b89

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m permitted status only
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
ab1daf12ad307e9c9e5ada8d7af3eb7c89578cb9

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m outside region deletion
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
617a8c53eda2b21dad81d2079d81c9b2736a9720

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m inside region deletion
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
1e2043e1914721b2a6eea55303aeffcb16ec25c5

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m head section edit
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
e9d74c67fa2b36bce879614c614b12a5e1eceb1a

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT add --all
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT -c user.name=CR02 Fixture -c user.email=cr02@example.invalid -c commit.gpgsign=false commit -q -m mixed permitted status and exempt head edit
exit=0

$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse HEAD
exit=0
a620716c567b8bd8981724680b1eec1cc076e8c0

MODULE /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py sha256=2b9285bfdeeeeda4ef763583ab1e869276ebd10202772630aaaca939f38ff4ee
$ module append-only-audit.audit('/fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT'); append-only-audit.exit_code(data)
exit=1
FILE_REGIONS ENTRY.md titles=[] prefixes=['## Errata']
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT log -1 --format=%s ab1daf12ad307e9c9e5ada8d7af3eb7c89578cb9
exit=0
permitted status only

EVENT permitted status only file=SOURCES.md deleted=1 graded=0 ungraded=0 permitted=1 status=ungraded
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT log -1 --format=%s 617a8c53eda2b21dad81d2079d81c9b2736a9720
exit=0
outside region deletion

EVENT outside region deletion file=ENTRY.md deleted=1 graded=0 ungraded=1 permitted=0 status=ungraded
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse 617a8c53eda2b21dad81d2079d81c9b2736a9720^1
exit=0
ab1daf12ad307e9c9e5ada8d7af3eb7c89578cb9

REGION_DELETION line='outside original' parent_section='## Body' inside=False
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT log -1 --format=%s 1e2043e1914721b2a6eea55303aeffcb16ec25c5
exit=0
inside region deletion

EVENT inside region deletion file=ENTRY.md deleted=1 graded=1 ungraded=0 permitted=0 status=unrestored
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT rev-parse 1e2043e1914721b2a6eea55303aeffcb16ec25c5^1
exit=0
617a8c53eda2b21dad81d2079d81c9b2736a9720

REGION_DELETION line='inside original' parent_section='## Errata' inside=True
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT log -1 --format=%s e9d74c67fa2b36bce879614c614b12a5e1eceb1a
exit=0
head section edit

EVENT head section edit file=SCORECARD.md deleted=1 graded=0 ungraded=1 permitted=0 status=ungraded
$ git -C /fast/scratch/hyaku/kama-r77/CR02AuditProbe/tmp.lNHTDINYcT log -1 --format=%s a620716c567b8bd8981724680b1eec1cc076e8c0
exit=0
mixed permitted status and exempt head edit

EVENT mixed permitted status and exempt head edit file=SOURCES.md deleted=2 graded=0 ungraded=1 permitted=1 status=ungraded
DECLARATIONS [{"declared_at": "NOTES.md:1", "ok": true, "path": "SOURCES.md", "reason": "", "region": "exempt"}, {"declared_at": "NOTES.md:2", "ok": true, "path": "ENTRY.md", "reason": "", "region": "only"}, {"declared_at": "NOTES.md:3", "ok": true, "path": "SCORECARD.md", "reason": "", "region": "exempt"}]
SUMMARY {"bad_declarations": 0, "bad_disclosures": 0, "binary": 0, "commits": 7, "disclosed": 0, "disclosed_lines": 0, "events": 5, "files": 3, "partial": 0, "permitted_lines": 2, "regressed": 0, "restored": 0, "ungraded": 4, "ungraded_lines": 3, "unmatched": 0, "unrestored": 1, "vanished": 0}
CLEANUP removed /fast/scratch/hyaku/kama-r77/CR02AuditProbe exists=False
```

No tools installed or updated. Scratch tree removed in Python `finally` after capturing receipt bytes in memory; no fixture remains.
