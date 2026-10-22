#!/usr/bin/env python3
"""Scratch-only candidate counter: committed fa3b62ae bytes plus the checks the
battery showed missing. Builds the candidate, then runs it on the same mutants
and on the earlier receipt. Predictions are written before the run."""
import pathlib
import subprocess
import sys

SCR = pathlib.Path("/fast/scratch/hyaku/kama-r25a2w2/RerunC2Counter")
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-25/a2-falsify/out/RerunC2Counter"

committed = (SCR / "count-c2.fa3b62ae.py").read_text()

NEW_FUNCS = '''NSLOT_LINE = re.compile(r"n_slots = (\\d+), n_ctx_slot = (\\d+), kv_unified = '(true|false)'")


def flag_value(argv, name):
    if name not in argv or argv.index(name) + 1 >= len(argv):
        return None
    return argv[argv.index(name) + 1]


def verdict_ok(c, d):
    """Candidate (scratch): the tool's own verdict plus cross-field facts."""
    if c.get("observed") is not True or c.get("error") is not None:
        return False
    t = c.get("teardown")
    if not (isinstance(t, dict) and t.get("port_closed") is True
            and is_int(t.get("child_returncode"))
            and t.get("ss_listen_lines_after") == []):
        return False
    srv = d.get("server")
    if not (isinstance(srv, dict) and isinstance(srv.get("sha256"), str)
            and c.get("server_sha256") == srv["sha256"]):
        return False
    argv = c["argv"]
    model = d.get("model")
    if not (flag_value(argv, "--port") == str(c.get("port"))
            and isinstance(model, dict)
            and flag_value(argv, "-m") == model.get("realpath")):
        return False
    slots = c["slots_n_ctx"]
    logged = [m.groups() for m in map(NSLOT_LINE.search, c["log_lines"]) if m]
    if not logged:
        return False
    ns, nc, _ = logged[-1]
    if int(ns) != c["total_slots"] or any(s != int(nc) for s in slots):
        return False
    if any(s != c["props_n_ctx"] for s in slots):
        return False
    if c.get("args") and c["id"].startswith("L"):
        for q in c["requests"]:
            if q.get("status") == 200 and (
                    q.get("tokens_predicted") != LOAD_REQUEST["n_predict"]
                    or q.get("truncated") is not False):
                return False
        if c["id"] in ("L1", "L2"):
            delta = c.get("concurrency_delta_s")
            if not (is_num(delta) and delta <= 0.05):
                return False
    return True


'''

A = "def main():"
B = '        if c.get("args") == args and cell_ok(c, kind):'
C = "    missing = [k for k in CELLS if k not in observed]"
for anchor in (A, B, C):
    assert committed.count(anchor) == 1, anchor
cand = committed.replace(A, NEW_FUNCS + A, 1)
cand = cand.replace(B, B[:-1] + " and verdict_ok(c, d):", 1)
cand = cand.replace(C, "    if not (isinstance(d, dict) and d.get(\"exit_code\") == 0\n            and d.get(\"error\") is None):\n        observed = []\n" + C, 1)
cand = cand.split("\n", 1)[0] + "\n# SCRATCH CANDIDATE (not registered): committed fa3b62ae counter plus verdict_ok checks.\n" + cand.split("\n", 1)[1]
(SCR / "count-c2.candidate.py").write_text(cand)
(OUT / "count-c2.candidate.py").write_text(cand)

# Load the battery definitions (everything before its run loop) without running it.
src = (SCR / "battery.py").read_text()
head = src.split("\nrows = []")[0]
exec(compile(head, str(SCR / "battery.py"), "exec"), globals())

COUNTERS_C = {"candidate": SCR / "count-c2.candidate.py"}
CAND_PRED = {
    "m00_base": "14 True []",
    "m01_observed_false_error_K1": "13 True ['K1']",
    "m02_port_still_listening_K2": "13 True ['K2']",
    "m03_error_only_K3": "13 True ['K3']",
    "m04_cell_server_sha_other_K4": "13 True ['K4']",
    "m05_cell_model_sha_other_K5": "14 False []",
    "m06_build_117550": "14 False []",
    "m07_pool_line_12048_K1": "13 True ['K1']",
    "m08_slots_fake_K1": "13 True ['K1']",
    "m09_props_fake_K2": "13 True ['K2']",
    "m10_argv_port_K6": "13 True ['K6']",
    "m11_argv_model_K7": "13 True ['K7']",
    "m12_L3_overlap": "13 True ['L3']",
    "m13_L2_status_503_one": "14 True []",
    "m14_L2_tokens_predicted_zero": "13 True ['L2']",
    "m15_drop_K8": "13 True ['K8']",
    "m16_dup_K1": "13 True ['K1']",
    "m17_args_K5_trailing_space": "13 True ['K5']",
    "m18_X2_observed_false_only": "13 True ['X2']",
    "m19_K4_child_returncode_null": "13 True ['K4']",
    "m20_top_exit_1_error": "0 True ['K1', 'K2', 'K3', 'K4', 'K5', 'K6', 'K7', 'K8', 'X1', 'X2', 'X3', 'L1', 'L2', 'L3']",
    "m21_total_slots_string_K1": "13 True ['K1']",
    "m22_props_bool_K1": "13 True ['K1']",
    "m23_pool_8_suffix_K1": "13 True ['K1']",
    "m24_no_server_version": "14 False []",
    "m25_slots_length_mismatch_K3": "13 True ['K3']",
    "m26_L1_three_requests": "13 True ['L1']",
    "m27_L2_no_timings": "13 True ['L2']",
    "m28_L2_status_700": "13 True ['L2']",
    "m29_top_model_sha_wrong": "14 False []",
}

lines = ["mutant\tcandidate_exit\tcandidate_result\tmatches_prediction"]
mismatch = 0
for name, fn in MUTANTS:
    d = copy.deepcopy(BASE)
    fn(d)
    path = MUT / f"{name}.json"
    path.write_text(json.dumps(d, ensure_ascii=False))
    rc, out, err = run(COUNTERS_C["candidate"], path)
    res = summary(out)
    ok = res == CAND_PRED[name]
    mismatch += (not ok)
    lines.append(f"{name}\t{rc}\t{res}\t{ok}" + ("" if ok else f"\t(predicted {CAND_PRED[name]})"))
lines.append("")
lines.append(f"candidate_prediction_mismatches={mismatch} of {len(MUTANTS)}")
rc, out, err = run(COUNTERS_C["candidate"], SCR / "receipt-5ea4fc44.json")
lines.append(f"history_5ea4fc44_candidate\texit={rc}\t{out}\tstderr={err!r}")
rc, out, err = run(COUNTERS_C["candidate"], SCR / "receipt-fa3b62ae.json")
lines.append(f"committed_receipt_candidate_direct\texit={rc}\t{out}\tstderr={err!r}")
lines.append(f"candidate_sha256_bytes={__import__('hashlib').sha256((SCR / 'count-c2.candidate.py').read_bytes()).hexdigest()}")
text = "\n".join(lines) + "\n"
(OUT / "candidate-battery.txt").write_text(text)
sys.stdout.write(text)
