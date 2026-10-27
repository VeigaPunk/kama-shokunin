#!/usr/bin/env python3
"""Sen1Exec probe: hand the live tool a memfd the kernel made non-executable
(MFD_NOEXEC_SEAL is exactly what vm.memfd_noexec >= 1 implies for a memfd_create()
call without MFD_EXEC). Same bytes, same seals plus F_SEAL_EXEC.

Question: does the tool fail closed with a clear reason, and does sealed_fd() even
notice? (sealed_fd tests seals & 15 == 15, size, digest - F_SEAL_EXEC is 32.)
"""
import fcntl, hashlib, json, os, subprocess, sys

SRC = "/home/vgpnk/.local/opt/llama-b11909/llama-server"
MODEL = "/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
F_ADD_SEALS, F_GET_SEALS = 1033, 1034
S = os.path.dirname(os.path.abspath(__file__))


def main():
    live = sys.argv[1]
    fd = os.memfd_create("llama-server", os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING
                         | 0x0008)  # MFD_NOEXEC_SEAL; os exposes no constant
    h = hashlib.sha256()
    with open(SRC, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            os.write(fd, chunk)
    fcntl.fcntl(fd, F_ADD_SEALS, 15)
    seals = fcntl.fcntl(fd, F_GET_SEALS)
    receipt = os.path.join(S, "receipt-noexec.json")
    p = subprocess.run([sys.executable, "-I", live, "--server", SRC, "--model", MODEL,
                        "--model-sha256", MODEL_SHA, "--alias", "kama-r48-live",
                        "--ctx", "64", "--threads", "1", "--server-fd", str(fd),
                        "--ready-timeout", "30", "--out", receipt],
                       capture_output=True, text=True, pass_fds=(fd,), timeout=120)
    out = {"seals": seals, "memfd_sha": h.hexdigest(), "exit": p.returncode,
           "stdout": p.stdout[-3000:], "stderr": p.stderr[-3000:],
           "receipt_written": os.path.exists(receipt)}
    if out["receipt_written"]:
        r = json.load(open(receipt))
        out["receipt_server_fd"] = (r.get("server") or {}).get("fd")
        out["receipt_errors"] = r.get("errors")
        out["receipt_server_exe"] = r.get("server_exe")
    print(json.dumps(out, indent=1))
    os.close(fd)


main()
