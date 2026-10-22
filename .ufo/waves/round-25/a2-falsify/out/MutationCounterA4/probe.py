#!/usr/bin/env python3
"""MutationCounterA4 probe: synthetic receipts that must NOT count under the
committed round-25 C2 counter (count-c2.py at fa3b62ae6475d111eb466d79af616aeebb08bbb9).

Every receipt is a copy of the committed receipt with one surgical change.
No llama-server child, no network, no lane production file is written.
"""
import copy
import hashlib
import json
import os
import subprocess
import sys

SCRATCH = os.path.dirname(os.path.abspath(__file__))
RECEIPT = os.path.join(SCRATCH, "receipt_pristine.json")
COUNTER = os.path.join(SCRATCH, "counter_pristine.py")
OUT = os.path.join(SCRATCH, "receipts")

BASE = json.load(open(RECEIPT))


def cell(rec, cid):
    for c in rec["cells"]:
        if c.get("id") == cid:
            return c
    raise KeyError(cid)


def slot_line(c):
    for l in c["log_lines"]:
        if "n_slots" in l:
            return l
    raise KeyError("no slot line")


# ---------------------------------------------------------------- mutations
def m_overlap_equal_times_L2(rec):
    """L2 (concurrent): the two requests carry identical start/end times."""
    c = cell(rec, "L2")
    c["requests"][1]["t_start"] = c["requests"][0]["t_start"]
    c["requests"][1]["t_end"] = c["requests"][0]["t_end"]
    return "L2: request[1] t_start/t_end copied from request[0] (equal times)"


def m_overlap_equal_times_L1(rec):
    c = cell(rec, "L1")
    c["requests"][1]["t_start"] = c["requests"][0]["t_start"]
    c["requests"][1]["t_end"] = c["requests"][0]["t_end"]
    return "L1: request[1] t_start/t_end copied from request[0] (equal times)"


def m_equal_start_only_L2(rec):
    c = cell(rec, "L2")
    c["requests"][1]["t_start"] = c["requests"][0]["t_start"]
    return "L2: request[1] t_start equal to request[0] t_start, t_end kept"


def m_equal_times_sequential_L3(rec):
    c = cell(rec, "L3")
    c["requests"][1]["t_start"] = c["requests"][0]["t_start"]
    c["requests"][1]["t_end"] = c["requests"][0]["t_end"]
    return "L3 (sequential cell): equal times on both requests"


def m_tstart_after_tend_L2(rec):
    c = cell(rec, "L2")
    c["requests"][0]["t_start"] = c["requests"][0]["t_end"] + 1.0
    return "L2: request[0] t_start = t_end + 1.0 (start after end)"


def m_tstart_after_tend_L1(rec):
    c = cell(rec, "L1")
    c["requests"][1]["t_end"] = c["requests"][1]["t_start"] - 1.0
    return "L1: request[1] t_end = t_start - 1.0 (start after end)"


def m_log_from_other_cell_K1(rec):
    """K1 carries K2's server log wholesale."""
    src = cell(rec, "K2")
    dst = cell(rec, "K1")
    dst["log_lines"] = copy.deepcopy(src["log_lines"])
    return "K1: log_lines replaced by K2's log lines (foreign cell log)"


def m_log_foreign_slot_line_K2(rec):
    """K2 keeps its own log but its n_slots line is replaced by K1's."""
    src = cell(rec, "K1")
    dst = cell(rec, "K2")
    old = slot_line(dst)
    foreign = slot_line(src)
    dst["log_lines"] = [foreign if l == old else l for l in dst["log_lines"]]
    return "K2: n_slots startup line replaced by K1's line (foreign log line)"


def m_argv_extra_after_K1(rec):
    c = cell(rec, "K1")
    c["argv"] = c["argv"] + ["--no-warmup"]
    return "K1: argv gains --no-warmup AFTER the registered args"


def m_argv_extra_before_K1(rec):
    c = cell(rec, "K1")
    argv = c["argv"]
    i = argv.index("-c")
    c["argv"] = argv[:i] + ["--no-context-shift"] + argv[i:]
    return "K1: argv gains --no-context-shift BEFORE the registered args"


def m_argv_extra_between_K2(rec):
    c = cell(rec, "K2")
    argv = c["argv"]
    i = argv.index("-c")
    c["argv"] = argv[:i] + ["--swa-full", "--no-mmap"] + argv[i:]
    return "K2: argv gains --swa-full --no-mmap BEFORE the registered args"


def m_slots_vs_log_K1(rec):
    """K1 claims 4 slots but its log says n_slots = 1, n_ctx_slot = 1024."""
    c = cell(rec, "K1")
    old = slot_line(c)
    new = old.replace("n_slots = 4", "n_slots = 1").replace(
        "n_ctx_slot = 2048", "n_ctx_slot = 1024")
    c["log_lines"] = [new if l == old else l for l in c["log_lines"]]
    return "K1: log says n_slots = 1, n_ctx_slot = 1024 but receipt claims total_slots 4 / slots_n_ctx [2048 x4]"


def m_nctx_slot_mismatch_K2(rec):
    c = cell(rec, "K2")
    old = slot_line(c)
    new = old.replace("n_ctx_slot = 1024", "n_ctx_slot = 2048")
    c["log_lines"] = [new if l == old else l for l in c["log_lines"]]
    return "K2: log n_ctx_slot = 2048 but slots_n_ctx says 1024"


def m_tokens_predicted_low_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["tokens_predicted"] = 12
    return "L2: both requests status 200 with tokens_predicted = 12 (below 600)"


def m_tokens_predicted_null_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["tokens_predicted"] = None
    return "L2: both requests status 200 with tokens_predicted = null"


def m_truncated_true_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["truncated"] = True
    return "L2: both requests status 200 with truncated = true"


def m_error_with_200_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["error"] = "Context size has been exceeded."
        q["error_type"] = "server_error"
    return "L2: both requests status 200 but carry a server error body"


def m_elapsed_inconsistent_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["t_end"] = q["t_start"] + 100.0
        q["elapsed_s"] = 0.174
    return "L2: t_end stretched to t_start+100 while elapsed_s stays 0.174 (overlap faked, elapsed ignored)"


def m_status_599_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["status"] = 599
    return "L2: HTTP status 599 (in range 100-599)"


def m_status_600_L2(rec):
    c = cell(rec, "L2")
    for q in c["requests"]:
        q["status"] = 600
    return "L2: HTTP status 600 (out of range)"


def m_cells_drift_L1(rec):
    rec["cells_drift"] = ["K1", "L2", "L3"]
    return "receipt-level cells_drift lists K1, L2, L3 (drift never read by the counter)"


def m_observed_false(rec):
    for c in rec["cells"]:
        c["observed"] = False
    return "every cell carries observed = false"


def m_model_path_swapped_K1(rec):
    c = cell(rec, "K1")
    argv = c["argv"]
    i = argv.index("-m")
    argv[i + 1] = "/home/vgpnk/.cache/kama-shokunin/models/other-model.gguf"
    return "K1: argv -m points at a different model file (model path never checked)"


def m_L1_both_200(rec):
    c = cell(rec, "L1")
    for q in c["requests"]:
        q["status"] = 200
        q["error"] = None
        q["error_type"] = None
        q["tokens_predicted"] = 600
        q["truncated"] = False
    return "L1: both requests status 200, no error (concurrency limit did not fire)"


def m_foreign_log_control_K4(rec):
    """Control for P07/P08: a foreign log whose pool number does NOT match."""
    src = cell(rec, "K1")
    dst = cell(rec, "K4")
    dst["log_lines"] = copy.deepcopy(src["log_lines"])
    return "CONTROL K4: log_lines replaced by K1's log (pool 2048 vs K4 kv_pool 1024)"


def m_stretch_L3_sequential(rec):
    """L3 is sequential; stretch t_end so the two intervals overlap."""
    c = cell(rec, "L3")
    for q in c["requests"]:
        q["t_end"] = q["t_start"] + 100.0
    return "L3: t_end stretched to t_start+100 so the intervals overlap (mode still sequential)"


def m_L2_elapsed_from_L3(rec):
    """L2 relabelled concurrent with fabricated overlapping times, but the
    independent elapsed_s witness is copied from the real sequential L3 run."""
    l2 = cell(rec, "L2")
    l3 = cell(rec, "L3")
    for i, q in enumerate(l2["requests"]):
        q["t_start"] = 6445.0 + i * 0.01
        q["t_end"] = 6445.5
        q["elapsed_s"] = l3["requests"][i]["elapsed_s"]
    return "L2: overlapping t_start/t_end fabricated, elapsed_s taken from the real sequential L3 run"


def m_L2_duplicate_request(rec):
    c = cell(rec, "L2")
    c["requests"][1] = copy.deepcopy(c["requests"][0])
    return "L2: request[1] is a byte-for-byte duplicate of request[0]"


def m_port_collision_K1_K2(rec):
    cell(rec, "K1")["port"] = cell(rec, "K2")["port"]
    return "K1 and K2 report the same port (47401); one server cannot serve both cells"


def m_slot_line_removed_K2(rec):
    c = cell(rec, "K2")
    old = slot_line(c)
    c["log_lines"] = [l for l in c["log_lines"] if l != old]
    return "K2: the n_slots startup line is removed from the log"
def m_L2_sequential_records_faked_overlap(rec):
    """L2 (concurrent) carries L3's REAL sequential request records, and a
    fake overlap is created by giving request[1] the same t_start as
    request[0] (equal times).  The real elapsed_s witnesses (0.125, 0.131)
    are kept, so the receipt says the two requests took ~0.13 s each but ran
    on the same interval -- physically impossible for two separate requests."""
    l2 = cell(rec, "L2")
    l3 = cell(rec, "L3")
    l2["requests"] = copy.deepcopy(l3["requests"])
    l2["requests"][1]["t_start"] = l2["requests"][0]["t_start"]
    return "L2: requests replaced by L3's real sequential records; request[1].t_start set equal to request[0].t_start (faked overlap, elapsed_s kept)"


def m_L2_sequential_records_verbatim(rec):
    """Control: L2 (concurrent) carries L3's REAL non-overlapping records
    verbatim.  The overlap check must reject this cell."""
    l2 = cell(rec, "L2")
    l3 = cell(rec, "L3")
    l2["requests"] = copy.deepcopy(l3["requests"])
    return "CONTROL L2: requests replaced by L3's real sequential records verbatim (no overlap)"


MUTANTS = [
    ("P01_overlap_equal_times_L2", m_overlap_equal_times_L2),
    ("P02_overlap_equal_times_L1", m_overlap_equal_times_L1),
    ("P03_equal_start_only_L2", m_equal_start_only_L2),
    ("P04_equal_times_sequential_L3", m_equal_times_sequential_L3),
    ("P05_tstart_after_tend_L2", m_tstart_after_tend_L2),
    ("P06_tstart_after_tend_L1", m_tstart_after_tend_L1),
    ("P07_log_from_other_cell_K1", m_log_from_other_cell_K1),
    ("P08_log_foreign_slot_line_K2", m_log_foreign_slot_line_K2),
    ("P09_argv_extra_after_args_K1", m_argv_extra_after_K1),
    ("P10_argv_extra_before_args_K1", m_argv_extra_before_K1),
    ("P11_argv_extra_before_args_K2", m_argv_extra_between_K2),
    ("P12_total_slots_vs_n_slots_log_K1", m_slots_vs_log_K1),
    ("P13_nctx_slot_mismatch_K2", m_nctx_slot_mismatch_K2),
    ("P14_l2_status200_tokens_predicted_12", m_tokens_predicted_low_L2),
    ("P15_l2_status200_tokens_predicted_null", m_tokens_predicted_null_L2),
    ("P16_l2_status200_truncated_true", m_truncated_true_L2),
    ("P17_l2_status200_with_error_body", m_error_with_200_L2),
    ("P18_l2_elapsed_vs_times_inconsistent", m_elapsed_inconsistent_L2),
    ("P19_l2_status_599", m_status_599_L2),
    ("P20_l2_status_600", m_status_600_L2),
    ("P21_receipt_cells_drift_nonempty", m_cells_drift_L1),
    ("P22_observed_false_everywhere", m_observed_false),
    ("P23_model_path_swapped_K1", m_model_path_swapped_K1),
    ("P24_L1_both_requests_status_200", m_L1_both_200),
    ("P25_control_foreign_log_K4_pool_mismatch", m_foreign_log_control_K4),
    ("P26_stretch_L3_sequential_to_overlap", m_stretch_L3_sequential),
    ("P27_L2_fabricated_overlap_elapsed_from_L3", m_L2_elapsed_from_L3),
    ("P28_L2_duplicate_request_object", m_L2_duplicate_request),
    ("P30_slot_line_removed_K2", m_slot_line_removed_K2),
    ("P31_L2_sequential_records_faked_overlap", m_L2_sequential_records_faked_overlap),
    ("P32_control_L2_sequential_records_verbatim", m_L2_sequential_records_verbatim),
]


def run_counter(path):
    p = subprocess.run([sys.executable, COUNTER, path], capture_output=True,
                       text=True, timeout=60)
    return {"stdout": p.stdout.rstrip("\n"), "stderr": p.stderr.rstrip("\n"),
            "exit_code": p.returncode}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    os.makedirs(OUT, exist_ok=True)
    results = {"counter": {"path": COUNTER, "sha256": sha(COUNTER)},
               "baseline_receipt": {"path": RECEIPT, "sha256": sha(RECEIPT)},
               "entries": []}

    # pristine baseline, run twice (pristine bytes) to prove the detector works
    base1 = run_counter(RECEIPT)
    base2 = run_counter(RECEIPT)
    results["baseline"] = {"run1": base1, "run2": base2,
                           "stable": base1 == base2}
    results["entries"].append({
        "name": "P00_pristine_receipt_control",
        "mutation": "none (committed receipt bytes, unmodified)",
        "description": "control: the committed receipt as committed",
        "expected": "observed 14 bound True missing []",
        "output": base1,
    })

    for name, fn in MUTANTS:
        rec = copy.deepcopy(BASE)
        desc = fn(rec)
        path = os.path.join(OUT, name + ".json")
        with open(path, "w") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        out = run_counter(path)
        results["entries"].append({
            "name": name,
            "mutation": desc,
            "description": desc,
            "receipt": path,
            "receipt_sha256": sha(path),
            "expected": "the mutated cell must be listed in missing (not counted)",
            "output": out,
        })

    # restoration proof: pristine receipt and counter bytes are untouched and
    # the counter still prints the same baseline line after every mutant run.
    after = run_counter(RECEIPT)
    results["restoration"] = {
        "counter_sha256_after": sha(COUNTER),
        "receipt_sha256_after": sha(RECEIPT),
        "counter_unchanged": sha(COUNTER) == results["counter"]["sha256"],
        "receipt_unchanged": sha(RECEIPT) == results["baseline_receipt"]["sha256"],
        "baseline_after": after,
        "baseline_reproduced": after == base1,
    }

    out_json = os.path.join(SCRATCH, "results.json")
    with open(out_json, "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)

    for e in results["entries"]:
        print("%-42s | %s | exit %s" % (e["name"], e["output"]["stdout"],
                                        e["output"]["exit_code"]))
    print("restoration:", json.dumps(results["restoration"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
