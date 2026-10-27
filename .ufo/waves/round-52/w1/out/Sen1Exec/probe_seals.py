#!/usr/bin/env python3
"""Sen1Exec probe 2: exactly what a same-uid process can do with the sealed image,
and whether sealed_fd()'s test (seals & 15, size, digest) is confined to memfds.

1. sealed memfd (what sealed_member makes, not executing): open O_WRONLY from another
   process -> write(2), pwrite(2), ftruncate(2), mmap(PROT_WRITE).
2. /dev/shm file (path-backed shmem): can it carry seals 15? If yes, an fd to it passes
   sealed_fd() while /proc/<pid>/exe names a path, not "/memfd:".
3. exec of /bin/true bytes from a sealed memfd: exec-ok, exit 0.
"""
import fcntl, hashlib, mmap, os, tempfile

F_ADD_SEALS, F_GET_SEALS = 1033, 1034
MFD_CLOEXEC, MFD_ALLOW_SEALING, MFD_NOEXEC_SEAL = 1, 2, 8
TRUE = open("/bin/true", "rb").read()


def fill_in(fd, data):
    off = 0
    while off < len(data):
        off += os.write(fd, data[off:])
    return len(data)


def attempt(fn):
    try:
        return {"ok": True, "value": fn()}
    except OSError as exc:
        return {"ok": False, "errno": exc.errno, "strerror": exc.strerror}


def exec_case(flags, label):
    fd = os.memfd_create("probe", flags)
    fill_in(fd, TRUE)
    fcntl.fcntl(fd, F_ADD_SEALS, 15)
    mode = os.fstat(fd).st_mode
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            os.execv(f"/proc/self/fd/{fd}", ["probe"])
        except OSError as exc:
            os.write(w, f"{exc.errno}:{exc.strerror}".encode())
            os._exit(97)
    os.close(w)
    msg = os.read(r, 200).decode()
    os.close(r)
    code = os.waitstatus_to_exitcode(os.waitpid(pid, 0)[1])
    os.close(fd)
    return {"label": label, "mode": oct(mode & 0o777), "exec": msg or "ok", "exit": code}


def main():
    out = {}
    data = b"sealed bytes" * 100
    fd = os.memfd_create("sealed", MFD_CLOEXEC | MFD_ALLOW_SEALING)
    fill_in(fd, data)
    fcntl.fcntl(fd, F_ADD_SEALS, 15)
    out["memfd_seals"] = fcntl.fcntl(fd, F_GET_SEALS)
    out["memfd_nlink"] = os.fstat(fd).st_nlink
    # another process (same uid) opens its /proc link for writing, then tries to change it
    wr = attempt(lambda: os.open(f"/proc/{os.getpid()}/fd/{fd}", os.O_WRONLY))
    out["open_O_WRONLY"] = {"ok": wr.get("ok"), "errno": wr.get("errno"), "strerror": wr.get("strerror")}
    if wr.get("ok"):
        h = wr["value"]
        out["write"] = attempt(lambda: os.write(h, b"X"))
        out["pwrite"] = attempt(lambda: os.pwrite(h, b"X", 0))
        out["ftruncate_smaller"] = attempt(lambda: os.ftruncate(h, 1))
        out["ftruncate_larger"] = attempt(lambda: os.ftruncate(h, len(data) + 4096))
        out["mmap_PROT_WRITE"] = attempt(lambda: mmap.mmap(h, 16, mmap.PROT_WRITE))
        out["add_seals_more"] = attempt(lambda: fcntl.fcntl(h, F_ADD_SEALS, 32))
        os.close(h)
    out["content_after"] = hashlib.sha256(os.pread(fd, len(data) + 4096, 0)).hexdigest()
    out["content_expected"] = hashlib.sha256(data).hexdigest()
    os.close(fd)
    # a path-backed shmem file, sealed like a memfd: does F_ADD_SEALS work there?
    d = tempfile.mkdtemp(dir="/dev/shm")
    p = os.path.join(d, "candidate")
    pathfd = os.open(p, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o755)
    fill_in(pathfd, TRUE)
    add = attempt(lambda: fcntl.fcntl(pathfd, F_ADD_SEALS, 15))
    out["path_backed"] = {"path": p, "add_seals": add,
                          "seals": attempt(lambda: fcntl.fcntl(pathfd, F_GET_SEALS)),
                          "nlink": os.fstat(pathfd).st_nlink,
                          "readlink": os.readlink(f"/proc/self/fd/{pathfd}")}
    os.close(pathfd)
    open(p, "rb").close()
    os.unlink(p)
    os.rmdir(d)
    out["exec_memfd_executable"] = exec_case(MFD_CLOEXEC | MFD_ALLOW_SEALING, "allow-sealing")
    out["exec_memfd_noexec"] = exec_case(MFD_CLOEXEC | MFD_ALLOW_SEALING | MFD_NOEXEC_SEAL,
                                        "noexec-seal")
    print(__import__("json").dumps(out, indent=1))


main()
