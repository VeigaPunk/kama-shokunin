#!/usr/bin/env python3
"""Measure the documented bind(:0)/release/rebind race in kama-llamacpp-live.py
pick_port(): two workers synchronously pick_port() then bind the offered port,
exactly like two concurrent replays would. Reports rounds where both were
offered the same port and rounds where the second bind failed (EADDRINUSE)."""
import importlib.util
import multiprocessing as mp
import os
import socket
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py"


def load():
    spec = importlib.util.spec_from_file_location("kama_live", LANE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def worker(barrier, rounds, out):
    mod = load()
    refused = mod.refused_ports()
    for rnd in range(rounds):
        barrier.wait()
        port = mod.pick_port(refused)
        ok = False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # llama-server's own bind: no SO_REUSEADDR permission to double-listen
            s.bind(("127.0.0.1", port))
            s.listen(1)
            ok = True
        except OSError as exc:
            out.put(("binderr", port, (rnd, exc.errno)))
        finally:
            if ok:
                s.close()
        out.put(("pick", port, (rnd, ok)))


def main():
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    ctx = mp.get_context("fork")
    barrier = ctx.Barrier(workers)
    q = ctx.Queue()
    ps = [ctx.Process(target=worker, args=(barrier, rounds, q)) for _ in range(workers)]
    for p in ps:
        p.start()
    picks = []
    errs = []
    for _ in range(rounds * workers):
        kind, port, x = q.get()
        if kind == "pick":
            picks.append((x[0], port))
        else:
            errs.append((x[0], port, x[1]))
    for p in ps:
        p.join()
    # group picks into rounds: queue order is per-worker interleaved, so compare
    # consecutive pairs as the concurrent window
    byround = {}
    for rnd, port in picks:
        byround.setdefault(rnd, []).append(port)
    dup = sum(1 for ports in byround.values() if len(set(ports)) != len(ports))
    print(f"portrace rounds={rounds} workers={workers} picks={len(picks)} "
          f"duplicate_offers={dup} bind_errors={len(errs)}")
    if errs:
        print("bind_errors:", errs[:10])
    print("sample:", [p for _, p in picks[:12]])


if __name__ == "__main__":
    main()
