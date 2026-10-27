#!/usr/bin/env python3
"""One witnessed replay with an inotify watcher on the witness dir: exact file
events (create / close_write / moved_from / moved_to / delete) for ready.json,
its per-run temp name and release. Uses libc inotify via ctypes (no package)."""
import ctypes
import json
import os
import struct
import sys
import threading
import time

sys.path.insert(0, "/fast/scratch/hyaku/kama-r50/X8WitnessPort")
import probe  # noqa: E402

IN_CLOSE_WRITE, IN_MOVED_FROM, IN_MOVED_TO, IN_CREATE, IN_DELETE = 0x8, 0x40, 0x80, 0x100, 0x200
MASK = IN_CLOSE_WRITE | IN_MOVED_FROM | IN_MOVED_TO | IN_CREATE | IN_DELETE
NAMES = {IN_CREATE: "CREATE", IN_CLOSE_WRITE: "CLOSE_WRITE",
         IN_MOVED_FROM: "MOVED_FROM", IN_MOVED_TO: "MOVED_TO",
         IN_DELETE: "DELETE"}
libc = ctypes.CDLL("libc.so.6", use_errno=True)


def watch(path, events, stop, t0):
    fd = libc.inotify_init1(os.O_NONBLOCK)
    if fd < 0:
        events.append({"err": "inotify_init1 failed %d" % ctypes.get_errno()})
        return
    wd = libc.inotify_add_watch(fd, path.encode(), MASK)
    if wd < 0:
        events.append({"err": "inotify_add_watch failed %d" % ctypes.get_errno()})
        return
    buf = ctypes.create_string_buffer(4096)
    while not stop.is_set():
        n = libc.read(fd, buf, 4096)
        if n <= 0:
            time.sleep(0.002)
            continue
        off = 0
        data = bytes(buf.raw[:n])
        while off + 16 <= len(data):
            _w, mask, _cookie, ln = struct.unpack_from("iIII", data, off)
            name = data[off + 16:off + 16 + ln].rstrip(b"\0").decode("utf-8", "replace")
            off += 16 + ln
            if mask & 0x40000000:  # IN_IGNORED
                continue
            events.append({"ms": round((time.monotonic() - t0) * 1000, 2),
                           "event": NAMES.get(mask & ~(0x40000000 | 0x8000000),
                                              "0x%x" % mask), "name": name})


def main():
    root = os.path.join(probe.S, "w1")
    w = os.path.join(root, "watch")
    probe.empty_dir(w)
    work = os.path.join(root, "watchwork")
    out = os.path.join(root, "watch.json")
    log = os.path.join(root, "watch.log")
    events, stop = [], threading.Event()
    t0 = time.monotonic()
    th = threading.Thread(target=watch, args=(w, events, stop, t0), daemon=True)
    th.start()
    p, argv, fh = probe.start_replay(work, out, w, 45, log)
    obs = probe.Observer("watch", w, p, timeout=180)
    obs.start()
    res = probe.finish(p, fh, out, "watch")
    obs.join(timeout=30)
    stop.set()
    th.join(timeout=5)
    dest = os.path.join(probe.RESULTS, "inotify.json")
    payload = {"witness_dir": w, "argv": argv, "exit": res["exit"],
               "replay": res["replay"], "rerun": res["rerun"],
               "observer": obs.summary(), "events": events,
               "dir_after": probe.listing(w), "t0_note": "ms since watcher start"}
    with open(dest, "w") as fh:
        json.dump(payload, fh, indent=1)
    for e in events:
        print(e)
    print("released_ms", obs.released_at, "gone_ms", obs.ready_gone_at,
          "match", (res["replay"] or {}).get("match"), "dir_after", payload["dir_after"])
    print("wrote", dest)


if __name__ == "__main__":
    main()
