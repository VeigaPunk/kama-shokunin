# FinalCase47 raw run log (postfix falsification, round 24)

Seat: FinalCase47 (leaf, no dispatch). Scope: PG48-opaque-unused-tree-no-unresolved-token.

## Pins (private clone, detached, tree clean)

    clone                /fast/scratch/hyaku/kama-r24/postfix/FinalCase47/clone
    clone source         /home/vgpnk/Projects/shokunin/kama-shokunin (read-only)
    clone command        git clone --no-hardlinks <source> clone
    detached commit      92063cfc60e217fa7e2098c568578119b16a1b95
    git status           clean (0 lines)
    tools/report-landing-audit.py            b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f
    tests/report-audit/promisor-grid.py      30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270
    tests/report-audit/promisor-grid-expectations.json
                                            d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1
    git 2.56.0, python 3.14.8; no tool installed for this seat

## A1 - primary grid cell (current arm, one cell only)

argv (cwd = clone):

    TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase47/tmp-grid \
    python3 tests/report-audit/promisor-grid.py --arm current \
      --case PG48-opaque-unused-tree-no-unresolved-token --json \
      --out /fast/scratch/hyaku/kama-r24/postfix/FinalCase47/out/grid-pg48

exit 0.

Row (candidate.json -> arms.current.rows[0]):

    case                 PG48-opaque-unused-tree-no-unresolved-token
    kind                 policy
    exit                 0
    met                  true      (met_amended true, met_original true)
    amended_problems     []
    original_problems    []
    defects / kinds      [] / []
    raw_defects          []
    objects_acquired     {"lane": [], "fleet": []}
    stderr_tail          ""
    traceback/internal_error/timed_out/leaked  false/false/false/false
    twin                 null      twin_equal null, twins null
    twin_pairs_in_manifest 0, twin_compared 0, twin_mismatch []
    expected (amended)   exit 0, kinds [], reason_class null, defects []
    expected (frozen)    exit 2, reason_class "metadata"  (not executed here)
    document.summary.status "clean", required 1, round_commits 1,
      by_kind all zero, defects 0
    population_sha256 612b0a74f3eebaa9074bdde8ecd8f194f55ebaf9a35ab2b975fddbff8dd2ed88
    population_size 47

## A2 - predeclared supplemental metadata companion (outside 47)

argv (cwd = seat scratch, TMPDIR = own tmp-supp):

    TMPDIR=/fast/scratch/hyaku/kama-r24/postfix/FinalCase47/tmp-supp \
    python3 supp-companion.py /fast/scratch/hyaku/kama-r24/postfix/FinalCase47/out/supp

exit 0. Script: supp-companion.py (copied here). It imports the pinned grid module
read-only and calls BUILDERS["c_opaque_unused_tree_clean"] on a fresh grid root,
so the fixture is the UNRUN fixture.

Fixture (builder c_opaque_unused_tree_clean = lane_mark="config", opaque_tree=True,
drop=("opaque_tree",)): lane commit 18089c6071793e8be726676c30371c68a837ca48; the
subtree "d" (2a675c1af91c97c51f5101d6cff10bb797458ab6) is dropped from the lane
store; the fleet report cites only the lane commit, so every cited token resolves.

Plain companion construction: shutil.copytree of the UNRUN fixture lane (filesystem
copy, no git clone of a partial store), then removal of ONLY the promisor metadata
the builder installed: config keys remote.origin.promisor and
extensions.partialclone (no .promisor markers exist in this config-marked lane);
remote.origin.url left byte-identical.

Attestation (supplemental-companion.json -> attestation):

    object_inventory_equal                true   (6 objects, --no-lazy-fetch
                                                  cat-file --batch-all-objects)
    object_pack_index_digests_equal       true   (7 files: .git/objects/** +
                                                  .git/index, sha256 per file)
    missing_objects_marked == _plain      true   ["2a675c1af91c97c51f5101d6cff10bb797458ab6"]
    missing_subtree_sha                   2a675c1af91c97c51f5101d6cff10bb797458ab6
    refs_equal                            true   refs/heads/master 18089c60...
    promisor_facts.marked.promisor_backed true    (config + promisor_true)
    promisor_facts.plain.promisor_backed  false   (config [], promisor_true [], markers [])
    origin_url_unchanged                  true
    origin_url_exists_on_disk             false  (as built: absent-remote.git)

Auditor runs on both metadata variants (pinned tools/report-landing-audit.py,
argv: --lane-repo <lane> --fleet-repo <fleet> --rounds 1 --json --no-errata):

    marked lane   exit 0  stderr ""  status clean  objects_acquired {lane:[],fleet:[]}
    plain  lane   exit 0  stderr ""  status clean  objects_acquired {lane:[],fleet:[]}
    normalized_documents_equal            true
    grid row document == marked document  true
    grid row document == plain  document  true

## Manifest read-only observations (no cell executed)

    unique registered twin pairs                         25
    pairs whose live (amended) exit is 2 on both sides    5
      PG13<->PG14, PG15<->PG16, PG17<->PG18, PG19<->PG20  (amendment-unchanged)
      PG33<->PG34  (PG34 is an amendment-changed member: original exit 1 -> amended 2)
    pairs whose live (amended) exit is 0 on both sides   12
    PG48 twin field                                     null
