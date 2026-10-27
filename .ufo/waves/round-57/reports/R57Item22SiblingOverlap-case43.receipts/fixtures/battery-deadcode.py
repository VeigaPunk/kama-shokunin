import sys
ROSTER = {
    "base-old-counter": {"designation": "control", "expected": "missed"},
    "round56-counter": {"designation": "positive-control", "expected": "detected"},
    "m-drop-ldaudit": {"designation": "kill", "expected": "missed"},
}

def _never_called():
    run('base-old-counter', None, 'missed', None)
    run('round56-counter', None, 'detected', None)
    run('m-drop-ldaudit', None, 'missed', None)


if __name__ == '__main__':
    print('dead-call: calls exist only in an uncalled function')
