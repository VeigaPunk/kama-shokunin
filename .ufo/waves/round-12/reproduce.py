#!/usr/bin/env python3
"""Round-12 C1 reproduction: exact-source correspondence, integrity, and controls.
Runs fidelity on old SOURCES (`--manifest none`), new SOURCES (explicit frozen
manifest), `--selftest`, coherent snapshot+manifest mutation, manifest-only pin
corruption, manifest repoint, and empty-repo source-unavailable. C1 counts only
a valid source anchor with unequal source bytes; pin failures are excluded.
Stdout-only JSON; no file is written. Exit 0 expected, 1 failed, 2 could-not-evaluate.
"""
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
WAVE = ROOT / ".ufo/waves/round-12"
FID, NEW = WAVE / "fidelity.py", WAVE / "frozen/corpus/SOURCES.md"
MAN, OLD = WAVE / "frozen/expected.json", ROOT / ".ufo/waves/round-11/frozen/before/corpus/SOURCES.md"
REV, SPATH = "2f7303c242319c1dc96c6bcf7702ac18b3ca1aad", "corpus/SOURCES.md"
SPEC = f"{REV}:{SPATH}"
OID = "7de1360655eadada356fe110813c6e1338142551"
SHA = "9dc40d25a595b3d42b39649e17094cfa4e7190cfbf340331252dd29dea22093a"
NBYTES = 18898
OLD_SHA = "52665cf2d648112be2683c61485d42da1bf1dc859ea1df41d857672c60142fa1"
ATTACK_REV = "fe57cc8a01acba9b6d7ed20e11b4914dfb68d903"
ATTACK_PATH = ".ufo/waves/round-11/frozen/before/corpus/SOURCES.md"
MAN_EXPECTED = {"schema": "kama-round-12-frozen/v1", "snapshot_path": SPATH,
                "snapshot_sha256": SHA, "source_revision": REV, "source_path": SPATH,
                "source_oid": OID, "source_sha256": SHA, "source_bytes": NBYTES,
                "expected_verdict": "clean"}
SELFTEST_NAMES = {"clean", "coherent-snapshot-and-manifest-mutation", "snapshot-tampered",
                  "pin-only-corruption-exact-snapshot", "source-unavailable",
                  "unpinned-matching-snapshot-is-not-clean", "unpinned-source-mismatch",
                  "manifest-cannot-redirect-anchor", "absent-explicit-manifest",
                  "snapshot-unavailable", "symlink-snapshot-rejected"}
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_NO_REPLACE_OBJECTS": "1", "GIT_NO_LAZY_FETCH": "1", "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
def run(cmd: list[object], keep: bool = True) -> tuple[dict, bytes]:
    argv = [str(part) for part in cmd]
    try:
        p = subprocess.run(argv, cwd=ROOT, env=ENV, capture_output=True, timeout=600,
                           check=False, shell=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"cmd": argv, "exit": None, "stdout": "", "stderr": f"{type(exc).__name__}: {exc}"}, b""
    return {"cmd": argv, "exit": p.returncode,
            "stdout": p.stdout.decode("utf-8", "replace") if keep else None,
            "stderr": p.stderr.decode("utf-8", "replace"), "stdout_bytes": len(p.stdout),
            "stdout_sha256": sha(p.stdout), "stderr_bytes": len(p.stderr),
            "stderr_sha256": sha(p.stderr)}, p.stdout
def git(*args: object, keep: bool = True) -> tuple[dict, bytes]:
    return run(["git", "--no-pager", "--no-replace-objects", "-C", ROOT, *args], keep=keep)
def main() -> int:
    errors: list[str] = []
    failures: list[str] = []
    records: dict[str, dict] = {}
    head1, _ = git("rev-parse", "HEAD")
    measured = (head1.get("stdout") or "").strip()
    if head1.get("exit") != 0:
        errors.append("HEAD before failed")
    for path, label in ((FID, "fidelity"), (NEW, "new snapshot"), (MAN, "manifest"), (OLD, "old snapshot")):
        if not path.is_file():
            errors.append(f"missing {label}: {path}")
    new = NEW.read_bytes() if NEW.is_file() else None
    old = OLD.read_bytes() if OLD.is_file() else None
    manifest: object = {}
    man_sha = None
    man_ok = False
    if MAN.is_file():
        raw = MAN.read_bytes()
        man_sha = sha(raw)
        try:
            manifest = json.loads(raw.decode("utf-8"))
            man_ok = manifest == MAN_EXPECTED
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"manifest invalid JSON: {exc}")
        if not man_ok:
            errors.append("manifest differs from pinned expected object")
    else:
        errors.append("default manifest unavailable")
    oid_rec, oid_b = git("rev-parse", "--verify", SPEC)
    blob_rec, blob = git("cat-file", "blob", SPEC, keep=False)
    src = sha(blob)
    source_checks = {
        "oid": oid_rec.get("exit") == 0 and oid_b.decode("utf-8", "replace").strip() == OID,
        "sha256": blob_rec.get("exit") == 0 and src == SHA,
        "bytes": blob_rec.get("exit") == 0 and len(blob) == NBYTES,
        "new_matches": new is not None and sha(new) == src,
        "new_pinned": new is not None and sha(new) == SHA,
        "old_differs": old is not None and sha(old) != src,
        "old_pinned": old is not None and sha(old) == OLD_SHA,
    }
    if not all(source_checks.values()):
        errors.append("independent source anchor/correspondence checks failed")
    def case(name: str, cmd: list[object], code: int, finding: str, mismatches: object = "skip",
             source_count: object = "skip", **fields: object) -> None:
        rec, _ = run(cmd)
        try:
            payload = json.loads(rec.get("stdout") or "")
        except json.JSONDecodeError:
            payload = {}
            errors.append(f"{name}: fidelity stdout is not JSON")
        obs = {k: payload.get(k) for k in ("finding", "mismatches", "source_anchor_matches",
               "source_matches", "pinned", "integrity", "integrity_result", "correspondence",
               "snapshot_pin_matches", "snapshot_sha256", "manifest_sha256")}
        derived = (1 if obs["source_anchor_matches"] is True and obs["source_matches"] is False
                   else 0 if obs["source_anchor_matches"] is True and obs["source_matches"] is True else None)
        checks = {"exit": rec.get("exit") == code, "finding": payload.get("finding") == finding,
                  "source_correspondence_mismatches": True if source_count == "skip" else derived == source_count}
        if mismatches != "skip":
            checks["mismatches"] = payload.get("mismatches") == mismatches
        for k, v in fields.items():
            checks[k] = k in payload and payload.get(k) == v
        rec.update(observed={**obs, "source_correspondence_mismatches": derived},
                   checks=checks, ok=all(checks.values()))
        records[name] = rec
        if not rec["ok"]:
            failures.append(name)
            if (isinstance(payload.get("finding"), str)
                    and payload.get("finding") in {"snapshot_unavailable", "manifest_invalid", "source_unavailable",
                                                   "unpinned", "internal_error"}
                    and payload.get("finding") != finding):
                errors.append(f"{name}: could-not-evaluate {payload['finding']}")
    if FID.is_file() and old is not None:
        case("before", [sys.executable, FID, "--snapshot", OLD, "--manifest", "none", "--repo", ROOT],
             1, "source_mismatch", 1, 1, pinned=False, integrity="not_checked",
             integrity_result="not_checked", correspondence="mismatch", snapshot_pin_matches=None,
             source_matches=False, source_anchor_matches=True, snapshot_sha256=OLD_SHA)
    if FID.is_file() and new is not None:
        case("after", [sys.executable, FID, "--snapshot", NEW, "--manifest", MAN, "--repo", ROOT],
             0, "clean", 0, 0, pinned=True, integrity="checked", integrity_result="match",
             correspondence="match", snapshot_pin_matches=True, source_matches=True,
             source_anchor_matches=True, snapshot_sha256=SHA, manifest_sha256=man_sha)
    st_rec, _ = run([sys.executable, FID, "--selftest"])
    try:
        st = json.loads(st_rec.get("stdout") or "")
    except json.JSONDecodeError:
        st = {}
        errors.append("selftest stdout is not JSON")
    items = st.get("checks") if isinstance(st.get("checks"), list) else []
    names = {x.get("name") for x in items if isinstance(x, dict)}
    st_ok = (st_rec.get("exit") == 0 and st.get("schema") == "kama-round-12-selftest/v1"
             and st.get("passed") == 11 and st.get("failed") == 0 and names == SELFTEST_NAMES
             and all(x.get("ok") is True for x in items if isinstance(x, dict)))
    st_rec.update(observed={"passed": st.get("passed"), "failed": st.get("failed"),
                            "names": sorted(names), "checks": len(items)},
                  checks={"selftest": st_ok}, ok=st_ok)
    records["selftest"] = st_rec
    if not st_ok:
        errors.append("selftest: expected 11 named cases, all ok, exit 0")
    if man_ok and new is not None and old is not None and FID.is_file():
        with tempfile.TemporaryDirectory(prefix="kama-round12-controls-") as raw:
            t = Path(raw)
            mut = new + b"\ncoherent-mutation-marker\n"
            ms = sha(mut)
            (t / "cs").write_bytes(mut)
            cm = dict(manifest)
            cm["snapshot_sha256"] = ms
            (t / "cm").write_text(json.dumps(cm), encoding="utf-8")
            case("coherent", [sys.executable, FID, "--snapshot", t / "cs", "--manifest", t / "cm", "--repo", ROOT],
                 1, "source_mismatch", 1, 1, pinned=True, integrity="checked", integrity_result="match",
                 correspondence="mismatch", snapshot_pin_matches=True, source_matches=False,
                 source_anchor_matches=True, snapshot_sha256=ms, manifest_sha256=sha((t / "cm").read_bytes()))
            (t / "ts").write_bytes(new)
            tm = dict(manifest)
            tm["snapshot_sha256"] = "0" * 64
            (t / "tm").write_text(json.dumps(tm), encoding="utf-8")
            case("tamper", [sys.executable, FID, "--snapshot", t / "ts", "--manifest", t / "tm", "--repo", ROOT],
                 2, "snapshot_tampered", 0, 0, pinned=True, integrity="checked", integrity_result="mismatch",
                 correspondence="match", snapshot_pin_matches=False, source_matches=True,
                 source_anchor_matches=True, snapshot_sha256=SHA, manifest_sha256=sha((t / "tm").read_bytes()))
            (t / "rs").write_bytes(old)
            rm = dict(manifest)
            rm.update({"snapshot_sha256": sha(old), "source_revision": ATTACK_REV, "source_path": ATTACK_PATH})
            (t / "rm").write_text(json.dumps(rm), encoding="utf-8")
            case("repoint", [sys.executable, FID, "--snapshot", t / "rs", "--manifest", t / "rm", "--repo", ROOT],
                 2, "manifest_invalid", pinned=False, integrity="not_checked", integrity_result="not_checked")
            (t / "empty").mkdir()
            run(["git", "--no-replace-objects", "-C", t / "empty", "init", "-q"])
            case("unavailable", [sys.executable, FID, "--snapshot", NEW, "--manifest", MAN, "--repo", t / "empty"],
                 2, "source_unavailable", 0, None, pinned=True, integrity="checked", integrity_result="match",
                 correspondence="unavailable", snapshot_pin_matches=True, source_matches=None,
                 source_anchor_matches=None, snapshot_sha256=SHA)
    else:
        failures.append("controls")
    head2, _ = git("rev-parse", "HEAD")
    head_ok = (head1.get("exit") == 0 and head2.get("exit") == 0
               and head1.get("stdout") == head2.get("stdout"))
    if not head_ok:
        errors.append("HEAD unavailable or changed during run")
    required = ("before", "after", "selftest", "coherent", "tamper", "repoint", "unavailable")
    all_ok = all(name in records and records[name].get("ok") for name in required)
    code = 2 if errors else (0 if all_ok and man_ok and all(source_checks.values()) and head_ok else 1)
    before = records.get("before", {}).get("observed", {})
    after = records.get("after", {}).get("observed", {})
    claim = {name: {"exit": records.get(name, {}).get("exit"), "finding": observed.get("finding"),
                    "source_anchor_matches": observed.get("source_anchor_matches"),
                    "source_matches": observed.get("source_matches"),
                    "source_correspondence_mismatches": observed.get("source_correspondence_mismatches")}
             for name, observed in (("before", before), ("after", after))}
    b, a = claim["before"]["source_correspondence_mismatches"], claim["after"]["source_correspondence_mismatches"]
    claim["source_correspondence_mismatches"] = {"before": b, "after": a,
                                                 "delta": b - a if isinstance(b, int) and isinstance(a, int) else None}
    receipt = {
        "schema": "kama-round-12-reproduction/v1",
        "pinned": {"revision": REV, "path": SPATH, "blob_oid": OID, "sha256": SHA,
                   "bytes": NBYTES, "old_snapshot_sha256": OLD_SHA},
        "measured_commit": measured, "head_before": head1, "head_after": head2,
        "manifest": {"path": str(MAN), "sha256": man_sha, "expected": MAN_EXPECTED,
                     "observed": manifest, "ok": man_ok},
        "source": {"oid_record": oid_rec, "blob_record": blob_rec,
                   "oid": oid_b.decode("utf-8", "replace").strip() if oid_rec.get("exit") == 0 else None,
                   "sha256": src, "bytes": len(blob), "checks": source_checks},
        "records": records, "claim": claim, "failures": failures, "errors": errors,
        "ok": code == 0, "exit": code,
    }
    print(json.dumps(receipt, indent=2))
    return code
if __name__ == "__main__":
    sys.exit(main())
