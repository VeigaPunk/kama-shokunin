BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")


def env_leg(pid, probs):
    probs.append(f"env: environ of pid {pid} unreadable")
    return None
