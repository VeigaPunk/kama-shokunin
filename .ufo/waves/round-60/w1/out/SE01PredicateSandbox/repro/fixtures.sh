# Reproduce every measurement in the SE01PredicateSandbox report (round 60, kama).
# All work happens in a scratch dir; the lane tree is only ever read.
set -u
S=${S:-/fast/scratch/hyaku/kama-r60/SE01PredicateSandbox}
LANE=/home/vgpnk/Projects/shokunin/kama-shokunin
export TMPDIR=$S
mkdir -p "$S/cases" "$S/cases2" "$S/cases4"
cd "$S"

# 0. exact tip copy of the instrument under test (never import it from the lane dir:
#    importing would create __pycache__ inside the read-only lane tree)
git -C "$LANE" show 11f2d667:tools/round60-c2-counter.py > round60-c2-counter.py
sha256sum round60-c2-counter.py    # d2e9a722416b8e482224dc2e6e17ced14bb87fb0ebd7de4464b04776b86a8fe5
cp "$LANE/.ufo/waves/round-60/live/receipt.json" receipt.json

# 1. every probe runs bounded, as the seat spec requires
run() { ( ulimit -v 2000000; timeout 10 python3 -B driver.py "$1" full ) 2>&1 | tail -1; }

# 2. fixtures: built deterministically by repro/build_fixtures.py (asserts toplevel before
#    the first commit, identity passed per command)
python3 repro/build_fixtures.py "$S"
# fixA: one row whose predicate is a 100k-deep subscript chain -> parser RecursionError
# fixB: one row whose predicate is the 181-byte nested-comprehension bomb
# fixC: valid receipt whose capture body is 200k-deep nested JSON arrays
# fixD: 14 rows over a 14-line population, row 0 = the bomb   (measured 254 859 ms, met=True)
# fixE: 4 rows, 2 population lines, one row uses a genexp whose body reads c (silent drop)
# fixF: same shape as fixD, every predicate cheap             (measured 418 ms, met=True)
#
# Build recipe used for each (verbatim, one per fixture):
#   python3 - "$S" <<'PY' ... writes SKILL.md, registry/ollama-live-claims-r60.tsv,
#   .ufo/waves/round-60/live/receipt.json ...
#   PY
#   D=$S/fixA.XXXXXX; git -C "$D" init -q
#   test "$(git -C "$D" rev-parse --show-toplevel)" = "$D" || exit 1
#   git -C "$D" add -A
#   git -C "$D" -c user.name=fixture -c user.email=fixture@localhost commit -qm fixture
# (the identity is passed per-command, never written to any config; only fixture repos)

# 3. the four decisive runs
for D in fixA.0wGKyl fixC fixB fixF fixD; do
  ( ulimit -v 2000000; timeout 300 python3 -B round60-c2-counter.py --repo "$S/$D" --tip HEAD --base HEAD ) 2>&1 | tail -3
done
# fixA  -> traceback, RecursionError at ast.parse, exit 1, no summary line
# fixC  -> traceback, RecursionError in receipt_caps/json.loads, exit 1, no summary line
# fixB  -> summary met=False after 12 689 ms (predicate credited: sensitive=1/1)
# fixF  -> summary met=True in 418 ms
# fixD  -> summary met=True in 254 859 ms   (same registry shape, one 181-byte predicate)

# 4. same fixtures against the proposed patch (scratch copy only; the lane is not edited)
for D in fixA.0wGKyl fixC fixB fixE; do
  ( ulimit -v 2000000; timeout 300 python3 -B counter-patched.py --repo "$S/$D" --tip HEAD --base HEAD ) 2>&1 | tail -1
done
# fixA -> errors=1 met=False (224 ms) ; fixC -> receipt_ok=1 met=False ; fixB -> errors=1 met=False (212 ms)
# fixE -> covered=2/2 evaluated=2  (tip: covered=1/2 evaluated=1)

# 5. call-count amplification (instrumented, cheap predicate, R rows over R population lines)
#    R=1 -> 13 evaluate calls ; R=5 -> 365 ; R=14 -> 2912 ; R=20 -> 5960 ; R=28 -> 11704
