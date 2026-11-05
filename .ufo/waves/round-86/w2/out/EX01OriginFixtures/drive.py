"""EX01 fixture driver for round86-pin-origin.py (C3). Scratch-only; writes receipts to OUT."""
import functools
import hashlib
import http.server
import json
import pathlib
import subprocess
import threading

S = pathlib.Path("/fast/scratch/hyaku/kama-r86/EX01OriginFixtures")
FIX = S / "fixture"
WWW = S / "www"
OUT = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/w2/out/EX01OriginFixtures")
TOOL = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round86-pin-origin.py"
ROWS = "registry/pin-recheck-rows.tsv"
HEADER = ("engine", "ref", "newest", "verdict", "date", "quote_pin", "line_pin",
          "quote_newest", "line_newest", "extract_pin", "extract_newest", "note")

# ---- upstream fixture bodies (served by the local server, one dir per case)
UP_LF = "L1 title\nL2 public endpoint statement\nL3 middle\nL4 tail statement\nL5 end\nL6 last\n"


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(WWW))

    class Quiet(handler.func):  # noqa
        def log_message(self, *a, **k):
            pass

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(WWW)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def put_upstream(rel, data: bytes):
    p = WWW / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)


def anchor(url, ref, start, end, body: str, sha=None, header=None):
    b = body.encode()
    digest = sha or hashlib.sha256(b).hexdigest()
    head = header if header is not None else f"# url={url} sha256={digest} ref={ref} lines={start}-{end}"
    return (head + "\n").encode() + b


def write_case(name, files, row_pin, row_newest, rows_override=None):
    for rel, data in files.items():
        p = FIX / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    reg = FIX / ROWS
    reg.parent.mkdir(parents=True, exist_ok=True)
    if rows_override is not None:
        reg.write_bytes(rows_override)
    else:
        cells = ["fixture", "v1", "v2", "holds", "2026-11-04", "q", "2", "q", "2",
                 row_pin, row_newest, "EX01 fixture"]
        reg.write_bytes(("\t".join(HEADER) + "\n" + "\t".join(cells) + "\n").encode())
    git = ["git", "-C", str(FIX)]
    top = subprocess.check_output(git + ["rev-parse", "--show-toplevel"], text=True).strip()
    assert top == str(FIX), (top, FIX)
    subprocess.check_call(git + ["add", "-A"])
    subprocess.check_call(git + ["-c", "user.name=ex01", "-c", "user.email=ex01@fixture.invalid",
                                 "commit", "-q", "--allow-empty", "-m", f"ex01 case {name}"])
    return subprocess.check_output(git + ["rev-parse", "HEAD"], text=True).strip()


def run_tool(rev, case):
    proc = subprocess.run(["python3", TOOL, "--repo", str(FIX), "--rev", rev],
                          capture_output=True, text=True, cwd=str(S), env={"TMPDIR": str(S), "PATH": "/usr/bin:/bin:/usr/local/bin"} | {k: v for k, v in __import__("os").environ.items() if k in ("HOME", "LANG", "LC_ALL")})
    rec = {"case": case, "rev": rev, "argv": ["python3", TOOL, "--repo", str(FIX), "--rev", rev],
           "exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
    (OUT / f"{case}.out").write_text(proc.stdout)
    (OUT / f"{case}.err").write_text(proc.stderr)
    return rec


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    srv, port = serve()
    base = f"http://127.0.0.1:{port}"
    results = []
    # shared upstream file for the first five required cases
    put_upstream("up/README.md", UP_LF.encode())
    u = f"{base}/up/README.md"
    good_body = "L2 public endpoint statement\nL3 middle\nL4 tail statement\n"

    # (a) byte-identical
    files = {
        "corpus/anchors/a.txt": anchor(u, "v1", 2, 4, good_body).replace(b"", b"", 0),
        "corpus/anchors/b.txt": anchor(u, "v2", 2, 4, good_body),
    }
    rev = write_case("a-identical", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "a-identical"))

    # (b) fabricated but hash-consistent (header digest matches the fake body; bytes differ from upstream)
    fake = "L2 public endpoint statement\nL3 FABRICATED middle\nL4 tail statement\n"
    files = {
        "corpus/anchors/a.txt": anchor(u, "v1", 2, 4, good_body),
        "corpus/anchors/b.txt": anchor(u, "v2", 2, 4, fake),
    }
    rev = write_case("b-fabricated-hash-consistent", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "b-fabricated-hash-consistent"))

    # (c) digest lie: header digest is all zeros, body is genuine upstream bytes
    files = {
        "corpus/anchors/a.txt": anchor(u, "v1", 2, 4, good_body),
        "corpus/anchors/b.txt": anchor(u, "v2", 2, 4, good_body, sha="0" * 64),
    }
    rev = write_case("c-digest-lie", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "c-digest-lie"))

    # (d) range outside upstream (upstream has 6 lines; declared 5-99)
    body_d = "L5 end\nL6 last\n"
    files = {
        "corpus/anchors/a.txt": anchor(u, "v1", 2, 4, good_body),
        "corpus/anchors/b.txt": anchor(u, "v2", 5, 99, body_d),
    }
    rev = write_case("d-range-outside", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "d-range-outside"))

    # (e) malformed header: digest field is 3 hex chars, not 64
    files = {
        "corpus/anchors/a.txt": anchor(u, "v1", 2, 4, good_body),
        "corpus/anchors/b.txt": anchor(u, "v2", 2, 4, good_body,
                                       header=f"# url={u} sha256=abc ref=v2 lines=2-4"),
    }
    rev = write_case("e-malformed-header", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "e-malformed-header"))

    # ---- extra falsification probes (beyond the five named cases)
    # X1 CRLF upstream; committed anchor body is the LF form of the same lines
    put_upstream("crlf/README.md", b"L1\r\nL2 crlf\r\nL3 crlf\r\nL4\r\n")
    uc = f"{base}/crlf/README.md"
    files = {
        "corpus/anchors/a.txt": anchor(uc, "v1", 2, 3, "L2 crlf\nL3 crlf\n"),
        "corpus/anchors/b.txt": anchor(uc, "v2", 2, 3, "L2 crlf\nL3 crlf\n"),
    }
    rev = write_case("x1-crlf-upstream-lf-body", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "x1-crlf-upstream-lf-body"))

    # X2 upstream last line without trailing newline; body adds "\n" (stored convention)
    put_upstream("nonl/README.md", b"L1\nL2 nonl\nL3 nonl")
    un = f"{base}/nonl/README.md"
    files = {
        "corpus/anchors/a.txt": anchor(un, "v1", 2, 3, "L2 nonl\nL3 nonl\n"),
        "corpus/anchors/b.txt": anchor(un, "v2", 2, 3, "L2 nonl\nL3 nonl\n"),
    }
    rev = write_case("x2-upstream-no-final-newline", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "x2-upstream-no-final-newline"))

    # X3 form feed inside upstream line 2: str.splitlines() splits it, split("\n") does not
    put_upstream("ff/README.md", b"L1\nL2 before\x0cFF-AFTER\nL3\n")
    uf = f"{base}/ff/README.md"
    files = {
        "corpus/anchors/a.txt": anchor(uf, "v1", 2, 2, "FF-AFTER\n"),
        "corpus/anchors/b.txt": anchor(uf, "v2", 2, 2, "FF-AFTER\n"),
    }
    rev = write_case("x3-formfeed-line-split", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "x3-formfeed-line-split"))
    # X3b form feed splits a LF line under str.splitlines(); declared LF line 3 is "L3",
    # the fabricated body "BBB" is the splitlines fragment of line 2 and is graded verified
    put_upstream("ffb/README.md", b"L1\nAAA\x0cBBB\nL3\n")
    ufb = f"{base}/ffb/README.md"
    files = {
        "corpus/anchors/a.txt": anchor(ufb, "v1", 3, 3, "BBB\n"),
        "corpus/anchors/b.txt": anchor(ufb, "v2", 3, 3, "BBB\n"),
    }
    rev = write_case("x3b-formfeed-fabricated-body", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "x3b-formfeed-fabricated-body"))


    # X4 inverted range lines=4-2 with body "\n" (blank line) - window is empty + "\n"
    put_upstream("inv/README.md", UP_LF.encode())
    ui = f"{base}/inv/README.md"
    files = {
        "corpus/anchors/a.txt": anchor(ui, "v1", 4, 2, "\n"),
        "corpus/anchors/b.txt": anchor(ui, "v2", 2, 4, good_body),
    }
    rev = write_case("x4-inverted-range-blank-body", files, "corpus/anchors/a.txt", "corpus/anchors/b.txt")
    results.append(run_tool(rev, "x4-inverted-range-blank-body"))

    # X5 register with header only (all rows removed) - exit code of an empty grade
    header_only = ("\t".join(HEADER) + "\n").encode()
    rev = write_case("x5-header-only-register", {}, "", "", rows_override=header_only)
    results.append(run_tool(rev, "x5-header-only-register"))

    # X6 control: pristine selftest of the same tool
    st = subprocess.run(["python3", TOOL, "--selftest"], capture_output=True, text=True, cwd=str(S),
                        env={"TMPDIR": str(S), "PATH": "/usr/bin:/bin:/usr/local/bin"})
    (OUT / "selftest.out").write_text(st.stdout)
    (OUT / "selftest.err").write_text(st.stderr)
    results.append({"case": "selftest", "exit": st.returncode, "stdout": st.stdout, "stderr": st.stderr})

    srv.shutdown()
    (OUT / "summary.json").write_text(json.dumps(
        [{k: r[k] for k in ("case", "rev", "exit") if k in r} | {"stdout": r["stdout"]} if "stdout" in r else r
         for r in results], indent=2))
    for r in results:
        print(r["case"], "exit=", r["exit"], "rev=", r.get("rev", "-"))
        print("   " + r["stdout"].strip().replace("\n", "\n   "))
        if r.get("stderr", "").strip():
            print("   STDERR: " + r["stderr"].strip().replace("\n", "\n   "))


if __name__ == "__main__":
    main()
