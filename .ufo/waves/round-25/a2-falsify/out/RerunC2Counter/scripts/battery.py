#!/usr/bin/env python3
"""Negative-control battery for the round-25 C2 counter (scratch only).

Each mutant is one edit to the committed receipt bytes (blob 516f4600).
Both counter byte sets are run on every mutant as separate processes.
Predictions are written here before the run and compared after it.
"""
import copy
import json
import pathlib
import re
import subprocess
import sys

SCR = pathlib.Path("/fast/scratch/hyaku/kama-r25a2w2/RerunC2Counter")
LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-25/a2-falsify/out/RerunC2Counter"
COUNTERS = {
    "committed_fa3b62ae": SCR / "count-c2.fa3b62ae.py",
    "amend2_5388b7cf": SCR / "count-c2.5388b7cf.py",
}
BASE = json.loads((SCR / "receipt-fa3b62ae.json").read_text())
MUT = SCR / "mutants"
MUT.mkdir(exist_ok=True)


def cell(d, cid):
    return next(c for c in d["cells"] if c["id"] == cid)


def drop(d, cid):
    d["cells"] = [c for c in d["cells"] if c["id"] != cid]


def pool_sub(c, new_value):
    out = []
    for x in c["log_lines"]:
        out.append(re.sub(r"(llama_context: n_ctx\s+=\s+)2048(\s*)$",
                          lambda m: m.group(1) + str(new_value) + m.group(2), x))
    c["log_lines"] = out


def m00_base(d):
    pass


def m01_observed_false_error_K1(d):
    c = cell(d, "K1"); c["observed"] = False; c["error"] = "forced: test error"


def m02_port_still_listening_K2(d):
    c = cell(d, "K2"); c["observed"] = False
    c["teardown"]["port_closed"] = False
    c["teardown"]["child_returncode"] = None
    c["teardown"]["ss_listen_lines_after"] = ["LISTEN 0 4096 127.0.0.1:47401"]


def m03_error_only_K3(d):
    c = cell(d, "K3"); c["observed"] = False; c["error"] = "ready-timeout"


def m04_cell_server_sha_other_K4(d):
    cell(d, "K4")["server_sha256"] = "0" * 64


def m05_cell_model_sha_other_K5(d):
    cell(d, "K5")["model_sha256"] = "0" * 64


def m06_build_117550(d):
    d["server_version"] = d["server_version"].replace("build 11755,", "build 117550,")


def m07_pool_line_12048_K1(d):
    pool_sub(cell(d, "K1"), 12048)


def m08_slots_fake_K1(d):
    cell(d, "K1")["slots_n_ctx"] = [1, 1, 1, 1]


def m09_props_fake_K2(d):
    cell(d, "K2")["props_n_ctx"] = 7


def m10_argv_port_K6(d):
    a = cell(d, "K6")["argv"]; a[a.index("--port") + 1] = "47999"


def m11_argv_model_K7(d):
    a = cell(d, "K7")["argv"]; a[a.index("-m") + 1] = "/tmp/other.gguf"


def m12_L3_overlap(d):
    q = cell(d, "L3")["requests"]; q[1]["t_start"] = q[0]["t_start"] + 0.01


def m13_L2_status_503_one(d):
    cell(d, "L2")["requests"][0]["status"] = 503


def m14_L2_tokens_predicted_zero(d):
    for q in cell(d, "L2")["requests"]:
        q["tokens_predicted"] = 0


def m15_drop_K8(d):
    drop(d, "K8")


def m16_dup_K1(d):
    d["cells"].append(copy.deepcopy(cell(d, "K1")))


def m17_args_K5_trailing_space(d):
    cell(d, "K5")["args"] = "-c 4096 -np 1 "


def m18_X2_observed_false_only(d):
    cell(d, "X2")["observed"] = False


def m19_K4_child_returncode_null(d):
    cell(d, "K4")["teardown"]["child_returncode"] = None


def m20_top_exit_1_error(d):
    d["exit_code"] = 1; d["error"] = "forced: test error"


def m21_total_slots_string_K1(d):
    cell(d, "K1")["total_slots"] = "4"


def m22_props_bool_K1(d):
    cell(d, "K1")["props_n_ctx"] = True


def m23_pool_8_suffix_K1(d):
    cell(d, "K1")["kv_pool_n_ctx"] = 8


def m24_no_server_version(d):
    del d["server_version"]


def m25_slots_length_mismatch_K3(d):
    cell(d, "K3")["slots_n_ctx"] = [2048]


def m26_L1_three_requests(d):
    c = cell(d, "L1"); c["requests"].append(copy.deepcopy(c["requests"][0]))


def m27_L2_no_timings(d):
    for q in cell(d, "L2")["requests"]:
        q.pop("t_start", None); q.pop("t_end", None)


def m28_L2_status_700(d):
    cell(d, "L2")["requests"][0]["status"] = 700


def m29_top_model_sha_wrong(d):
    d["model_sha256"] = "0" * 64


# predicted (committed_fa3b62ae, amend2_5388b7cf) -> (observed, bound, missing)
PRED = {
    "m00_base": ("14 True []", "14 True []"),
    "m01_observed_false_error_K1": ("14 True []", "14 True []"),
    "m02_port_still_listening_K2": ("14 True []", "14 True []"),
    "m03_error_only_K3": ("14 True []", "14 True []"),
    "m04_cell_server_sha_other_K4": ("14 True []", "14 True []"),
    "m05_cell_model_sha_other_K5": ("14 False []", "14 False []"),
    "m06_build_117550": ("14 False []", "14 True []"),
    "m07_pool_line_12048_K1": ("13 True ['K1']", "14 True []"),
    "m08_slots_fake_K1": ("14 True []", "14 True []"),
    "m09_props_fake_K2": ("14 True []", "14 True []"),
    "m10_argv_port_K6": ("14 True []", "14 True []"),
    "m11_argv_model_K7": ("14 True []", "14 True []"),
    "m12_L3_overlap": ("13 True ['L3']", "14 True []"),
    "m13_L2_status_503_one": ("14 True []", "14 True []"),
    "m14_L2_tokens_predicted_zero": ("14 True []", "14 True []"),
    "m15_drop_K8": ("13 True ['K8']", "13 True ['K8']"),
    "m16_dup_K1": ("13 True ['K1']", "13 True ['K1']"),
    "m17_args_K5_trailing_space": ("13 True ['K5']", "13 True ['K5']"),
    "m18_X2_observed_false_only": ("14 True []", "14 True []"),
    "m19_K4_child_returncode_null": ("14 True []", "14 True []"),
    "m20_top_exit_1_error": ("14 True []", "14 True []"),
    "m21_total_slots_string_K1": ("13 True ['K1']", "13 True ['K1']"),
    "m22_props_bool_K1": ("13 True ['K1']", "13 True ['K1']"),
    "m23_pool_8_suffix_K1": ("13 True ['K1']", "14 True []"),
    "m24_no_server_version": ("14 False []", "14 False []"),
    "m25_slots_length_mismatch_K3": ("13 True ['K3']", "14 True []"),
    "m26_L1_three_requests": ("13 True ['L1']", "14 True []"),
    "m27_L2_no_timings": ("13 True ['L2']", "14 True []"),
    "m28_L2_status_700": ("13 True ['L2']", "14 True []"),
    "m29_top_model_sha_wrong": ("14 False []", "14 False []"),
}

MUTANTS = [
    ("m00_base", m00_base), ("m01_observed_false_error_K1", m01_observed_false_error_K1),
    ("m02_port_still_listening_K2", m02_port_still_listening_K2),
    ("m03_error_only_K3", m03_error_only_K3),
    ("m04_cell_server_sha_other_K4", m04_cell_server_sha_other_K4),
    ("m05_cell_model_sha_other_K5", m05_cell_model_sha_other_K5),
    ("m06_build_117550", m06_build_117550),
    ("m07_pool_line_12048_K1", m07_pool_line_12048_K1),
    ("m08_slots_fake_K1", m08_slots_fake_K1), ("m09_props_fake_K2", m09_props_fake_K2),
    ("m10_argv_port_K6", m10_argv_port_K6), ("m11_argv_model_K7", m11_argv_model_K7),
    ("m12_L3_overlap", m12_L3_overlap), ("m13_L2_status_503_one", m13_L2_status_503_one),
    ("m14_L2_tokens_predicted_zero", m14_L2_tokens_predicted_zero),
    ("m15_drop_K8", m15_drop_K8), ("m16_dup_K1", m16_dup_K1),
    ("m17_args_K5_trailing_space", m17_args_K5_trailing_space),
    ("m18_X2_observed_false_only", m18_X2_observed_false_only),
    ("m19_K4_child_returncode_null", m19_K4_child_returncode_null),
    ("m20_top_exit_1_error", m20_top_exit_1_error),
    ("m21_total_slots_string_K1", m21_total_slots_string_K1),
    ("m22_props_bool_K1", m22_props_bool_K1),
    ("m23_pool_8_suffix_K1", m23_pool_8_suffix_K1),
    ("m24_no_server_version", m24_no_server_version),
    ("m25_slots_length_mismatch_K3", m25_slots_length_mismatch_K3),
    ("m26_L1_three_requests", m26_L1_three_requests),
    ("m27_L2_no_timings", m27_L2_no_timings), ("m28_L2_status_700", m28_L2_status_700),
    ("m29_top_model_sha_wrong", m29_top_model_sha_wrong),
]


def run(counter, receipt):
    p = subprocess.run([sys.executable, str(counter), str(receipt)],
                       capture_output=True, text=True, cwd=str(LANE))
    return p.returncode, p.stdout.strip(), p.stderr.strip()[:300]


def summary(stdout):
    m = re.match(r"registered (\d+) observed (\d+) bound (\w+) missing (\[.*\])", stdout)
    if not m:
        return stdout
    return f"{m.group(2)} {m.group(3)} {m.group(4)}"


rows = []
for name, fn in MUTANTS:
    d = copy.deepcopy(BASE)
    fn(d)
    path = MUT / f"{name}.json"
    path.write_text(json.dumps(d, ensure_ascii=False))
    row = {"mutant": name}
    for label, counter in COUNTERS.items():
        rc, out, err = run(counter, path)
        row[label] = (rc, summary(out), out, err)
    rows.append(row)

hist = {}
hist_path = SCR / "receipt-5ea4fc44.json"
for label, counter in COUNTERS.items():
    hist[label] = run(counter, hist_path)

lines = []
lines.append("mutant\tcommitted_exit\tcommitted_result\tcommitted_matches_prediction\tamend2_exit\tamend2_result\tamend2_matches_prediction")
mismatch = 0
for r in rows:
    pc = PRED[r["mutant"]]
    cr = r["committed_fa3b62ae"]; ar = r["amend2_5388b7cf"]
    cm = cr[1] == pc[0]; am = ar[1] == pc[1]
    mismatch += (not cm) + (not am)
    lines.append(f"{r['mutant']}\t{cr[0]}\t{cr[1]}\t{cm}\t{ar[0]}\t{ar[1]}\t{am}")
lines.append("")
lines.append(f"prediction_mismatches={mismatch} of {2 * len(rows)}")
lines.append("")
lines.append("history control receipt 5ea4fc44 (earlier receipt, expected committed 11 per amendment 4):")
for label, (rc, out, err) in hist.items():
    lines.append(f"  {label}\texit={rc}\t{out}\tstderr={err!r}")
lines.append("")
lines.append("full stdout/stderr per run:")
for r in rows:
    for label in COUNTERS:
        rc, s, out, err = r[label]
        lines.append(f"  {r['mutant']} {label} exit={rc} stdout={out!r} stderr={err!r}")
text = "\n".join(lines) + "\n"
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "battery.txt").write_text(text)
(SCR / "battery.txt").write_text(text)
sys.stdout.write(text)
