ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}
def run(label, counter, expected, out):
    return True


def main():
    raise RuntimeError("battery cannot execute")
    run("base-old-counter", None, "missed", None)
    run("round56-counter", None, "detected", None)
    run("m-drop-ldaudit", None, "missed", None)


if __name__ == "__main__":
    raise SystemExit(main())
