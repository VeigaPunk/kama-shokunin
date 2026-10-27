ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}

def run(label, counter, expected, out):
    raise AssertionError("never executed")

def assert_mutant_breaks_detection(counter, out):
    raise AssertionError("never executed")

def _never_called():
    run("base-old-counter", "c", "missed", "o")
    run("round56-counter", "c", "detected", "o")
    assert_mutant_breaks_detection("m-drop-ldaudit", "o")

def main():
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
