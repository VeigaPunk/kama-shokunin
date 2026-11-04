# MT01Binding — subject-round mutation probe

Axes: operability (owning-arm detection), calibration (scope and exact receipts), restoration (byte identity).

Frozen claims read in full. Scratch HEAD: `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`. No production edits, commits, network requests, or tool installations.
EX01 delivery was absent at initial discovery and the one mid-run poll. Therefore this probes a hand-written minimal implementation of the frozen spec over HEAD, retained as `spec-binding.py`; it does **not** certify EX01’s eventual replacement.

Baseline: selftest exit 0, `APPEND_DEBT_SELFTEST pass=31 fail=0`. The required negative fixture exits 1 with exactly one subject-mismatch finding; that expected negative exit is not a baseline failure. Its unrelated round-83 count-short remains.

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=2 bad_rows=1 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING note-wrong-deletion-round late line 2: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: deletion round 78 differs from subject round 79
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: missing 1
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

## Results

| Mutant | Selftest exit | Result | Owning arm / fixture behavior |
|---|---:|---|---|
| M1 remove binding | 1 | killed | `note-subject-mismatch` red; fixture mismatch vanishes (`bad_rows=0`) |
| M2 compare deletion to accepting | 0 | escaped | mismatch arm remains green because 78 differs from both 79 and 81; fixture rejects 113 rows rather than 1 |
| M3 replace != with < | 0 | escaped | fixture and arm exercise deletion 78 < subject 79 only; larger incorrect deletion is uncovered |
| M4 remove continue | 0 | escaped | class and exit still match; wrong row also covers its debt, fixture unaccepted falls 2→1 |
| M5 None is mismatch | 1 | killed by unresolvable arm, NOT mismatch arm | `note-subject-unresolvable` red; fixture unchanged because all its subjects resolve |

The instruction that every mutant must turn `note-subject-mismatch` red is not satisfied: M2/M3/M4 escape, and M5 is killed by the separate owning unresolvable arm. No contract changes were made.

## Exact selftest failures and mutant fixture output

### M1

Selftest exit 1; fixture exit 1.

```text
APPEND_DEBT_SELFTEST_FAIL note-subject-mismatch exit=0 want=1 summary={'events': 2, 'accepted': 1, 'late': 1, 'pending': 1, 'unaccepted': 0, 'bad_rows': 0, 'bad_declarations': 0, 'out_of_population': 0} findings=[]
APPEND_DEBT_SELFTEST pass=30 fail=1
```

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=1 bad_rows=0 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

### M2

Selftest exit 0; fixture exit 1.

```text
APPEND_DEBT_SELFTEST pass=31 fail=0
```

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=0 pending=0 unaccepted=23 bad_rows=113 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING note-wrong-deletion-round late line 2: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: deletion round 78 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 3: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 88d34850ef76373a0ed4f47b67be1013ad766a4d020999ab185004a150495a98: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 4: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 8e5a52b160aedcaee21b9bbb318a0951cbdd5cb6302691dc356bb7ea030dd4be: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 5: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 9488c25bf65fd039efffd761d07df6880ab9cc7bfe87966d7db6f05d4491f315: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 6: 223c881a3ae74679ed5c8cbc713f331f97a12338 SCORECARD.md 3eceadfb5e773755a3cbbdd4f93593ba60a0cebbc8f95d82c2810a3e7f7dbf90: deletion round 80 differs from subject round 80
APPEND_DEBT_FINDING note-wrong-deletion-round late line 7: 223c881a3ae74679ed5c8cbc713f331f97a12338 SCORECARD.md a0631296dd419fff2430de82f093510843e257a337eb68af0ccbab9046298c99: deletion round 80 differs from subject round 80
APPEND_DEBT_FINDING note-wrong-deletion-round late line 8: 28debbcf50c4cfe9ca6d3077508cc14aa8c7365a SCORECARD.md d894d647e7a7c4ca3bdcfa53bf112b0d39151573c157e006dcb839101838a449: deletion round 80 differs from subject round 80
APPEND_DEBT_FINDING note-wrong-deletion-round late line 9: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 1fcfaadf95a07eba33fcec70fc47826df7ddb42b7c92ba9eba6463727c84b1eb: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 10: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 33149e47836faca4f4dbea1694eb1b076d3846a0706ff54eaa6f4a54d667ff85: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 11: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 77281f66a047bba8c2dca1fe31dadb62f4b4ea8fc35fff63c18d853232479a90: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 12: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 9a659e0983714505d1dfe90e5ef35471d19d66f875ccd2b6a29aa0ba8f00f1f6: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 13: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md d6fc4a3a4c88d16958dd53e51fef3c407b4f37af9449b99f9a22d307dfa07a6b: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 14: 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md dc7e77a984ea25fd481d2b4d8462fec5988ce0b5fcbad9ea4613249834cd7afc: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 15: 4af44f78303f04a6ea32ea62cac586f89688d73a corpus/lessons/round-79.md 4f975e4f8555d4a7b1d8b29295958f04c603da9514c196427a95a51a63bb23f7: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 16: 4af44f78303f04a6ea32ea62cac586f89688d73a corpus/lessons/round-79.md d217400656a81df399157a05ec6d167fe28fc9c8cd5cb11ea6af239d12703785: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 17: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 00224a10d2750e62d2e1a718582a9b31e63487da0ab59fcb6ee5a7c0bf55e68a: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 18: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 016b426d7923200a4dedf191e628ca688f05f842dd4ce85edeb6a9256822e828: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 19: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 0aea4c628cd5f6a2c7512babd193553e43760bc84db0031831bf0ab7104b8204: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 20: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 1bd9ac171886b0b4dde91d0bcb92d1edbb715d7f7fe7e7ecd288736df942a6b1: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 21: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 28c4db37647094cab14d61bc56ac4d52ba84ffd0abbb28500dbc60e3e55879e0: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 22: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 323fdbb6422d37658b814e46d6da803b2c9a05f0724994a878bbceb24d777aa3: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 23: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 345ebdbc499430d3d8cd811ade5e95f457cfc73b3b0561e04128f5c910da7d36: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 24: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 38095c1fc74ec67142e1cc839babba6df57b8f07995834cee67e002913f82bf4: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 25: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3cc52e779ede31f87320f24c491f98b5be1c8a8f54e83b7305c2e0c77c756c5f: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 26: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3dfce508587e96d71ba72a70f4666aab1f9701c85832291c9cfbeefef497f899: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 27: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3e2ca423fd88328eb746c402ef1f957ed7670b594718aa8f5623ec1282a47745: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 28: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3e8bc8882cfb07550f5ccfeffb1887b3bd8f76404b47d4aa45c6b3b6b205c442: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 29: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 43cab9be584850ae8f0091a529b654786ef2e26910ff73673ae2e1b09903c0cb: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 30: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 4ad33c1d62d566d4d2a21a787e10c540995756e1b38b30e31c718f0a1caa3e10: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 31: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 4b919c983d204016c9d2619ed55c962b8372f397ac2cfdec0c8b6b89f2409926: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 32: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 514c7829720110402013ca877dc5345dbad8973531325b7ed776d91e9dad9a01: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 33: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 52183481f3d779f0c570f3fa953fbdad8f2fb569aa5f77f00539a6af68c4f626: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 34: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 53aa224b641d8ae50459f89e3cb1e1a617d5756e6721b13f62313550a75d055f: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 35: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 54d38c3615ff4e126255677b0b678fbcf3d81e6a4c622af227f895ce5cb57fad: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 36: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 78c6357966351f6bab678f1339368fc8b9ecf4c4cbd74651ce5026f5dc12dd90: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 37: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 7bff71c88f054b4056f6116024c79e077d7c4f9b972a94584ff76867a044d589: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 38: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 854fa756df0b8c9868f0c2721e6baeed6ed46eef6469eae221ce8a7a2dd0100b: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 39: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 86eb1e132a9aecff6ce8c7769a5961d023b49d3c8353de6b5019f0929c48b610: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 40: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 90990887ac56be8eb3567b39787c23ed583e5d5d082432ac4f530cf402ee635c: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 41: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 9a5f8a3281095546f4ffd237fcde84de3f58acf44b11ff9c44e607bed9eaae78: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 42: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv a4e5148705a70c6aa407641276527f096dd9fc714c1a1541a1c3cb1b0d4ee92d: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 43: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv a8b93414563b61040b23fb1356d8c0eb1674e0280f95bf57a70c6b228f618272: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 44: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv b78ac2a99410b4a3d322209d3a3163a10bc0c9c6f5ded760b25f99c36553868c: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 45: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv ce66c8699fa9e831b223e1eb7ba3c687de1fa0b972b5f5cd20275e22e8d928e4: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 46: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d142eea0d40da6810134c835a9b2266b4907910ab2ae976bc9a6ba97746e2d61: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 47: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d4f954ac1c00b4572ec16a2fdfeab23bfcbc9063f93f1dd4ca251bc14c5b90d3: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 48: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d6550eec84dc608175b973430ebcce20c9dbf7e14239e5726fe98275adfab355: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 49: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv df6871936c8e4db9e01668d1fc1d43cd99f00c88871f8ca86e520361ca9bec8e: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 50: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv e95fd8a4477f9bc0c95760d6d65891598705d53cc8ba6952e2d15bec5cb053f3: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 51: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv f4d016fadf0d7eba58cc54332f9f704fd45efdf49df598ff2a3d30c7b3573c57: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 52: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv f69d97613301756c5c74a6ddf6c15412587766372ce5de8c815f4197e53b1e26: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 53: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv fa01c60ff5fe6ef1bf5c16f2bf01878fd3e2a08ffbce4019a8dd9770279d0d1a: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 54: 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv fe598b53b78aacc1dae360346fc67b6a8240706c761e051fa02a56729994a8e2: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 55: 5fcef757a64e0e7736904c68e101d96f60a5d847 SCORECARD.md fe16f47e6176647849399e329e22b4ed7e7ac22c326638a691277364e0da5d5d: deletion round 80 differs from subject round 80
APPEND_DEBT_FINDING note-wrong-deletion-round late line 56: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 063920c3a6536193f3cb6f0478d7b299e475a96aa6e82e2dbd5a4b45538ba172: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 57: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 301bc0abf123faf3c04f57b4a8ad6a2704f0bc5c9ec46b0aefda791d9a746b0f: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 58: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 3bb8436b8d10f13068c93f3a33f0a69f966810d8dc392808ff5a807f2bfc7066: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 59: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 48fc535801a982a88503b3b8d07e92043251ac6db92ea26d2087b5220b548a7b: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 60: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 5c35cf3ffea710b202bf038b7a0e384684d15ce34e48b146637dc06703eda5bb: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 61: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 5eb14313275a36e19960d1de2f70a8bb8ddeb9d34da5a4bfacc7f1dc585ac461: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 62: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 70e89c06580a22f3130d685a8a44d283e6447a9a42597eb4358665cac91ca8b5: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 63: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 77e63cc6e3254667f30f22188f9f70afe4c157b8538ea9603606b7de31194cb4: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 64: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 7946464cbde8c7736e27224381107e16e2a07613f46473ca999f06469ac36a93: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 65: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 8236c0a453d72a39e88219969d430bb065125808865cc1268d85e4e00d04c253: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 66: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 825e504fb003d9b4d79eade8abb28f33351c5ef13acb542a53858e928da36de6: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 67: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ad8e8c16ada4cbb6d33be9efbd1862aa40b1cb80881a9dbd2784c638e263f15d: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 68: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md bece5465fa10c5a80fa98f6c7efa06b92f44f6517249d0a760c573d78f2c9dda: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 69: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ea41e185ee3e82d8e34424009dd91932a2cef8b1f795ac9162824b6f90a9d982: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 70: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ed3f13baaaba58344e0042dbae52c56df7d30ca40b093a50eeeb8632ab126177: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 71: 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md f8d311761565dfc0c5d451c24297ab809419f5d6ee0f5eae7fb094eef3f88f6d: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 72: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 07899019c2ce5b9056a3ab72b78a5d9437e2c30e6994b8daa382cad1efd28226: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 73: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 1be92dcfb05f4523ae7db98f141fb9de359aaa4bd540167716ba02ceec029410: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 74: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 220ce96fe482f534a0f60047eb00732d601ba1818bd27c02ee11475758c3d248: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 75: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 4759bb7b03347ad819e48b0654ac1e91c4ff6f18665bc218a83f1ff4d6a03676: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 76: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 4bef054ee00f74747a3e993e3f1250aa0a40b71fd22b1d6901fd2a943b712193: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 77: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 7987af60d8e29c76d8bc5d3eb0211e108eca09ec351c77d1450969fbeb6e2b2b: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 78: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 96a09376b1e0f2f8ee4c1eb43fdfd9e6576ddceb0a4a42125ee826b9fb4d6f2e: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 79: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md c694ca68fa12b3185cb4d4747e5a30a7a9b19b7bd68c4bd2a7a2136a8d037e42: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 80: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md cca48b38ee3278c2aef22951bb4ad625316efbd9e469ba815c1ef94b6dccc879: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 81: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md de63c835bff91b41fec40f4ac9aea5c5089d2590912408a14bcdbf1acf109df0: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 82: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md f05bc558d39bca9ad667075c1b22e3bab39f67db45b861a32ddda78077c93ccb: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 83: b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md f1a632eff9e0b126740ba1c447281fa2ec6e83db71f117a7c6bbab392485eda8: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 84: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 1db2175ef349fc5417ac07ff45ca7a24563eca00592d54d295aa996bcffb65f8: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 85: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 1e4ad651571c39c4c251b7922f844ee19a0c1b809767246496b3ba1f3831f814: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 86: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 28aebb27f2e3341206be3f165ae3635a898ada39eeb77688abcef12270dab940: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 87: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 85e94ef5bbd319becad18183ac0c05b5bb236fd9d3e0556180539c65a536ea8e: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 88: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md c5349039c8e8ee7e379c0bf17c77b76d80d0fd09d62002531870f96b94fb3111: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 89: f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md ca6a54bfdb3d06aeb87a353904753c94f867bf02593c7b23b68e893612f8f799: deletion round 79 differs from subject round 79
APPEND_DEBT_FINDING note-wrong-deletion-round late line 90: 017c34ca2d85fb547b3cd03961ce09fc43939993 SCORECARD.md 034bf734addb09bec685db45594d98bcae837acac9f4c2f5d55dd132403c304f: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 91: 37484391fa57b3376df68c01f92aca2b728550f7 SCORECARD.md 6f93595c3055cdb5f1c6c8a83c17a6b610af3da7a61d88e1d020502cdf9a5482: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 92: 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md 9a851e70a14128af4ebbde4390f7e233f6033aa0c60371983e440b84600ca654: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 93: 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md e61b0c5b01c8e56da93a1f4083d408c9a1b44c73a622a5529e83b27f3bcd35c8: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 94: 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md ffd60284ff50ef1ad43a4a23da5c451d4065479688f88248f46d55ef2ddb8b27: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 95: 93cdfd607b33fed4c052f3920bf867f32901f274 SCORECARD.md 125f327e63706c788a167f9bbde8c1fbc91de419e7dd498485b5603f88500afe: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 96: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 42a979310381141a43cced6295b15de642957ae2d418853fae21fef2abacebb9: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 97: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 64fb9076b410082403c4e3f13493d26362f1169e4e1a792e72796e57fa2b3dfc: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 98: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 708c1ee328c89f08687139df72d32eb4a815668a81cbb5681ecb88a844dd0a0b: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 99: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 81983db405e0a2f51c51610bbba5750b65b733bf5dc1d42568740d97050f172b: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 100: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md b6a2493109bbb392622737e33f32e44748f966550ee39adf5884d22ae0a422d2: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 101: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md c2962ff044f140d2549124171ba71816ccc04435889de8afb595603c352f8108: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 102: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md d91b278264ae00b8eff1aa4d11eec1e9069cb027a4a59866d2b35194f92082e0: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 103: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md e9196abbea3bf86c4c4473c6f9a488c72982a92e0d552ec5a1ba27e846680ba9: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 104: cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md fb2220584119ab0b67e0d9bc26e033ae5b386f545e10ec013565869c2ed677d4: deletion round 81 differs from subject round 81
APPEND_DEBT_FINDING note-wrong-deletion-round late line 105: 6a160310f621884e47fc4203347f6c82924c3619 SCORECARD.md ceb068b6d084097e40e1ba59180a243d746cfb52efc2c1039d5f4e5e26aadb68: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 106: 6a160310f621884e47fc4203347f6c82924c3619 SCORECARD.md fc49e99f5f58877a7c5d717de4e0fcc9f2c8fddcd2b108edb339421bc5a51b48: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 107: 7ad14e6cce65ab9c70fcb9855a9c94b5f917f638 SCORECARD.md 8b8522e37d3e0ae16f0bd8275586628869b43b894ea4f7524d40f942069f0410: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 108: 7ad14e6cce65ab9c70fcb9855a9c94b5f917f638 corpus/lessons/round-82.md e3ba2e63a6d7bc70945293ad120641be6cd655b1ec5b8790814cb505e53d8050: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 109: 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md 5833ea24e1e8d65095d2e6e12e434770031d8b60e6dddd455bf7af87bcffb805: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 110: 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md dda75682a31f06bb1c44f1a5298d351208a195c16a4b3474d8cdef9d1fb60e22: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 111: 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md f9f3609eec2522782fb739493cbaf205d5dae8e29e51362048407c4833b118a4: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 112: 962bd2513712d3d13e52b8fe2f65ece9a0003417 SCORECARD.md dd1f23fb9a7a23710eb9d8b5e8ba495e390575cabdb20f4f61b01c3265d7c555: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 113: 9efa6f1ce50f9afef23ed2ba4f6c0e913a33e308 SCORECARD.md 5f99129ed7cfc467016256188391854e157f598678e86d22bc6d5de27804716f: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING note-wrong-deletion-round late line 114: a251cbab6c3005fc9335631ea701f84192c6c55c SCORECARD.md 8053a48cfe94444b71fad5a88bd0c18d32cf4061ad840ad5af0c1f9d5709f2ad: deletion round 82 differs from subject round 82
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 063920c3a6536193f3cb6f0478d7b299e475a96aa6e82e2dbd5a4b45538ba172: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 301bc0abf123faf3c04f57b4a8ad6a2704f0bc5c9ec46b0aefda791d9a746b0f: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 3bb8436b8d10f13068c93f3a33f0a69f966810d8dc392808ff5a807f2bfc7066: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 48fc535801a982a88503b3b8d07e92043251ac6db92ea26d2087b5220b548a7b: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 5c35cf3ffea710b202bf038b7a0e384684d15ce34e48b146637dc06703eda5bb: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 5eb14313275a36e19960d1de2f70a8bb8ddeb9d34da5a4bfacc7f1dc585ac461: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 70e89c06580a22f3130d685a8a44d283e6447a9a42597eb4358665cac91ca8b5: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 77e63cc6e3254667f30f22188f9f70afe4c157b8538ea9603606b7de31194cb4: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 7946464cbde8c7736e27224381107e16e2a07613f46473ca999f06469ac36a93: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 8236c0a453d72a39e88219969d430bb065125808865cc1268d85e4e00d04c253: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md 825e504fb003d9b4d79eade8abb28f33351c5ef13acb542a53858e928da36de6: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ad8e8c16ada4cbb6d33be9efbd1862aa40b1cb80881a9dbd2784c638e263f15d: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md bece5465fa10c5a80fa98f6c7efa06b92f44f6517249d0a760c573d78f2c9dda: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ea41e185ee3e82d8e34424009dd91932a2cef8b1f795ac9162824b6f90a9d982: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md ed3f13baaaba58344e0042dbae52c56df7d30ca40b093a50eeeb8632ab126177: missing 1
APPEND_DEBT_FINDING count-short 9100605d6cfa2c467c1fd2468eef502f162e5d3d corpus/lessons/round-79.md f8d311761565dfc0c5d451c24297ab809419f5d6ee0f5eae7fb094eef3f88f6d: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 07899019c2ce5b9056a3ab72b78a5d9437e2c30e6994b8daa382cad1efd28226: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 1be92dcfb05f4523ae7db98f141fb9de359aaa4bd540167716ba02ceec029410: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 220ce96fe482f534a0f60047eb00732d601ba1818bd27c02ee11475758c3d248: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 4759bb7b03347ad819e48b0654ac1e91c4ff6f18665bc218a83f1ff4d6a03676: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 4bef054ee00f74747a3e993e3f1250aa0a40b71fd22b1d6901fd2a943b712193: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 7987af60d8e29c76d8bc5d3eb0211e108eca09ec351c77d1450969fbeb6e2b2b: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md 96a09376b1e0f2f8ee4c1eb43fdfd9e6576ddceb0a4a42125ee826b9fb4d6f2e: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md c694ca68fa12b3185cb4d4747e5a30a7a9b19b7bd68c4bd2a7a2136a8d037e42: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md cca48b38ee3278c2aef22951bb4ad625316efbd9e469ba815c1ef94b6dccc879: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md de63c835bff91b41fec40f4ac9aea5c5089d2590912408a14bcdbf1acf109df0: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md f05bc558d39bca9ad667075c1b22e3bab39f67db45b861a32ddda78077c93ccb: missing 1
APPEND_DEBT_FINDING count-short b574397576eaed3fbbf3568f102b8a2a155600d8 SCORECARD.md f1a632eff9e0b126740ba1c447281fa2ec6e83db71f117a7c6bbab392485eda8: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 1db2175ef349fc5417ac07ff45ca7a24563eca00592d54d295aa996bcffb65f8: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 1e4ad651571c39c4c251b7922f844ee19a0c1b809767246496b3ba1f3831f814: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 28aebb27f2e3341206be3f165ae3635a898ada39eeb77688abcef12270dab940: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md 85e94ef5bbd319becad18183ac0c05b5bb236fd9d3e0556180539c65a536ea8e: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md c5349039c8e8ee7e379c0bf17c77b76d80d0fd09d62002531870f96b94fb3111: missing 1
APPEND_DEBT_FINDING count-short f4a35f6c21778d03aa78fd9d05c6eb1b02d26b7f SCORECARD.md ca6a54bfdb3d06aeb87a353904753c94f867bf02593c7b23b68e893612f8f799: missing 1
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: missing 1
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 88d34850ef76373a0ed4f47b67be1013ad766a4d020999ab185004a150495a98: missing 1
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 8e5a52b160aedcaee21b9bbb318a0951cbdd5cb6302691dc356bb7ea030dd4be: missing 1
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 9488c25bf65fd039efffd761d07df6880ab9cc7bfe87966d7db6f05d4491f315: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 00224a10d2750e62d2e1a718582a9b31e63487da0ab59fcb6ee5a7c0bf55e68a: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 016b426d7923200a4dedf191e628ca688f05f842dd4ce85edeb6a9256822e828: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 0aea4c628cd5f6a2c7512babd193553e43760bc84db0031831bf0ab7104b8204: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 1bd9ac171886b0b4dde91d0bcb92d1edbb715d7f7fe7e7ecd288736df942a6b1: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 28c4db37647094cab14d61bc56ac4d52ba84ffd0abbb28500dbc60e3e55879e0: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 323fdbb6422d37658b814e46d6da803b2c9a05f0724994a878bbceb24d777aa3: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 345ebdbc499430d3d8cd811ade5e95f457cfc73b3b0561e04128f5c910da7d36: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 38095c1fc74ec67142e1cc839babba6df57b8f07995834cee67e002913f82bf4: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3cc52e779ede31f87320f24c491f98b5be1c8a8f54e83b7305c2e0c77c756c5f: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3dfce508587e96d71ba72a70f4666aab1f9701c85832291c9cfbeefef497f899: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3e2ca423fd88328eb746c402ef1f957ed7670b594718aa8f5623ec1282a47745: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 3e8bc8882cfb07550f5ccfeffb1887b3bd8f76404b47d4aa45c6b3b6b205c442: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 43cab9be584850ae8f0091a529b654786ef2e26910ff73673ae2e1b09903c0cb: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 4ad33c1d62d566d4d2a21a787e10c540995756e1b38b30e31c718f0a1caa3e10: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 4b919c983d204016c9d2619ed55c962b8372f397ac2cfdec0c8b6b89f2409926: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 514c7829720110402013ca877dc5345dbad8973531325b7ed776d91e9dad9a01: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 52183481f3d779f0c570f3fa953fbdad8f2fb569aa5f77f00539a6af68c4f626: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 53aa224b641d8ae50459f89e3cb1e1a617d5756e6721b13f62313550a75d055f: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 54d38c3615ff4e126255677b0b678fbcf3d81e6a4c622af227f895ce5cb57fad: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 78c6357966351f6bab678f1339368fc8b9ecf4c4cbd74651ce5026f5dc12dd90: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 7bff71c88f054b4056f6116024c79e077d7c4f9b972a94584ff76867a044d589: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 854fa756df0b8c9868f0c2721e6baeed6ed46eef6469eae221ce8a7a2dd0100b: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 86eb1e132a9aecff6ce8c7769a5961d023b49d3c8353de6b5019f0929c48b610: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 90990887ac56be8eb3567b39787c23ed583e5d5d082432ac4f530cf402ee635c: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv 9a5f8a3281095546f4ffd237fcde84de3f58acf44b11ff9c44e607bed9eaae78: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv a4e5148705a70c6aa407641276527f096dd9fc714c1a1541a1c3cb1b0d4ee92d: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv a8b93414563b61040b23fb1356d8c0eb1674e0280f95bf57a70c6b228f618272: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv b78ac2a99410b4a3d322209d3a3163a10bc0c9c6f5ded760b25f99c36553868c: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv ce66c8699fa9e831b223e1eb7ba3c687de1fa0b972b5f5cd20275e22e8d928e4: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d142eea0d40da6810134c835a9b2266b4907910ab2ae976bc9a6ba97746e2d61: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d4f954ac1c00b4572ec16a2fdfeab23bfcbc9063f93f1dd4ca251bc14c5b90d3: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv d6550eec84dc608175b973430ebcce20c9dbf7e14239e5726fe98275adfab355: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv df6871936c8e4db9e01668d1fc1d43cd99f00c88871f8ca86e520361ca9bec8e: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv e95fd8a4477f9bc0c95760d6d65891598705d53cc8ba6952e2d15bec5cb053f3: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv f4d016fadf0d7eba58cc54332f9f704fd45efdf49df598ff2a3d30c7b3573c57: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv f69d97613301756c5c74a6ddf6c15412587766372ce5de8c815f4197e53b1e26: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv fa01c60ff5fe6ef1bf5c16f2bf01878fd3e2a08ffbce4019a8dd9770279d0d1a: missing 1
APPEND_DEBT_FINDING count-short 5785cdff641fb210966c93168a6ff922b82af414 registry/append-only-accepted.tsv fe598b53b78aacc1dae360346fc67b6a8240706c761e051fa02a56729994a8e2: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 1fcfaadf95a07eba33fcec70fc47826df7ddb42b7c92ba9eba6463727c84b1eb: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 33149e47836faca4f4dbea1694eb1b076d3846a0706ff54eaa6f4a54d667ff85: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 77281f66a047bba8c2dca1fe31dadb62f4b4ea8fc35fff63c18d853232479a90: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md 9a659e0983714505d1dfe90e5ef35471d19d66f875ccd2b6a29aa0ba8f00f1f6: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md d6fc4a3a4c88d16958dd53e51fef3c407b4f37af9449b99f9a22d307dfa07a6b: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a SCORECARD.md dc7e77a984ea25fd481d2b4d8462fec5988ce0b5fcbad9ea4613249834cd7afc: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a corpus/lessons/round-79.md 4f975e4f8555d4a7b1d8b29295958f04c603da9514c196427a95a51a63bb23f7: missing 1
APPEND_DEBT_FINDING count-short 4af44f78303f04a6ea32ea62cac586f89688d73a corpus/lessons/round-79.md d217400656a81df399157a05ec6d167fe28fc9c8cd5cb11ea6af239d12703785: missing 1
APPEND_DEBT_FINDING count-short 28debbcf50c4cfe9ca6d3077508cc14aa8c7365a SCORECARD.md d894d647e7a7c4ca3bdcfa53bf112b0d39151573c157e006dcb839101838a449: missing 1
APPEND_DEBT_FINDING count-short 5fcef757a64e0e7736904c68e101d96f60a5d847 SCORECARD.md fe16f47e6176647849399e329e22b4ed7e7ac22c326638a691277364e0da5d5d: missing 1
APPEND_DEBT_FINDING count-short 223c881a3ae74679ed5c8cbc713f331f97a12338 SCORECARD.md 3eceadfb5e773755a3cbbdd4f93593ba60a0cebbc8f95d82c2810a3e7f7dbf90: missing 1
APPEND_DEBT_FINDING count-short 223c881a3ae74679ed5c8cbc713f331f97a12338 SCORECARD.md a0631296dd419fff2430de82f093510843e257a337eb68af0ccbab9046298c99: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 42a979310381141a43cced6295b15de642957ae2d418853fae21fef2abacebb9: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 64fb9076b410082403c4e3f13493d26362f1169e4e1a792e72796e57fa2b3dfc: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 708c1ee328c89f08687139df72d32eb4a815668a81cbb5681ecb88a844dd0a0b: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md 81983db405e0a2f51c51610bbba5750b65b733bf5dc1d42568740d97050f172b: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md b6a2493109bbb392622737e33f32e44748f966550ee39adf5884d22ae0a422d2: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md c2962ff044f140d2549124171ba71816ccc04435889de8afb595603c352f8108: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md d91b278264ae00b8eff1aa4d11eec1e9069cb027a4a59866d2b35194f92082e0: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md e9196abbea3bf86c4c4473c6f9a488c72982a92e0d552ec5a1ba27e846680ba9: missing 1
APPEND_DEBT_FINDING count-short cf28c47074f9bb48c8a8e7397bba58791478dc48 SCORECARD.md fb2220584119ab0b67e0d9bc26e033ae5b386f545e10ec013565869c2ed677d4: missing 1
APPEND_DEBT_FINDING count-short 37484391fa57b3376df68c01f92aca2b728550f7 SCORECARD.md 6f93595c3055cdb5f1c6c8a83c17a6b610af3da7a61d88e1d020502cdf9a5482: missing 1
APPEND_DEBT_FINDING count-short 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md 9a851e70a14128af4ebbde4390f7e233f6033aa0c60371983e440b84600ca654: missing 1
APPEND_DEBT_FINDING count-short 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md e61b0c5b01c8e56da93a1f4083d408c9a1b44c73a622a5529e83b27f3bcd35c8: missing 1
APPEND_DEBT_FINDING count-short 50c711ece84cbb911bec763a20c102038f942d0a SCORECARD.md ffd60284ff50ef1ad43a4a23da5c451d4065479688f88248f46d55ef2ddb8b27: missing 1
APPEND_DEBT_FINDING count-short 93cdfd607b33fed4c052f3920bf867f32901f274 SCORECARD.md 125f327e63706c788a167f9bbde8c1fbc91de419e7dd498485b5603f88500afe: missing 1
APPEND_DEBT_FINDING count-short 017c34ca2d85fb547b3cd03961ce09fc43939993 SCORECARD.md 034bf734addb09bec685db45594d98bcae837acac9f4c2f5d55dd132403c304f: missing 1
APPEND_DEBT_FINDING count-short 962bd2513712d3d13e52b8fe2f65ece9a0003417 SCORECARD.md dd1f23fb9a7a23710eb9d8b5e8ba495e390575cabdb20f4f61b01c3265d7c555: missing 1
APPEND_DEBT_FINDING count-short a251cbab6c3005fc9335631ea701f84192c6c55c SCORECARD.md 8053a48cfe94444b71fad5a88bd0c18d32cf4061ad840ad5af0c1f9d5709f2ad: missing 1
APPEND_DEBT_FINDING count-short 7ad14e6cce65ab9c70fcb9855a9c94b5f917f638 SCORECARD.md 8b8522e37d3e0ae16f0bd8275586628869b43b894ea4f7524d40f942069f0410: missing 1
APPEND_DEBT_FINDING count-short 7ad14e6cce65ab9c70fcb9855a9c94b5f917f638 corpus/lessons/round-82.md e3ba2e63a6d7bc70945293ad120641be6cd655b1ec5b8790814cb505e53d8050: missing 1
APPEND_DEBT_FINDING count-short 6a160310f621884e47fc4203347f6c82924c3619 SCORECARD.md ceb068b6d084097e40e1ba59180a243d746cfb52efc2c1039d5f4e5e26aadb68: missing 1
APPEND_DEBT_FINDING count-short 6a160310f621884e47fc4203347f6c82924c3619 SCORECARD.md fc49e99f5f58877a7c5d717de4e0fcc9f2c8fddcd2b108edb339421bc5a51b48: missing 1
APPEND_DEBT_FINDING count-short 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md 5833ea24e1e8d65095d2e6e12e434770031d8b60e6dddd455bf7af87bcffb805: missing 1
APPEND_DEBT_FINDING count-short 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md dda75682a31f06bb1c44f1a5298d351208a195c16a4b3474d8cdef9d1fb60e22: missing 1
APPEND_DEBT_FINDING count-short 8a3e8af2b37ff680cf2f574c4767c0fba69403cf SCORECARD.md f9f3609eec2522782fb739493cbaf205d5dae8e29e51362048407c4833b118a4: missing 1
APPEND_DEBT_FINDING count-short 9efa6f1ce50f9afef23ed2ba4f6c0e913a33e308 SCORECARD.md 5f99129ed7cfc467016256188391854e157f598678e86d22bc6d5de27804716f: missing 1
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

### M3

Selftest exit 0; fixture exit 1.

```text
APPEND_DEBT_SELFTEST pass=31 fail=0
```

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=2 bad_rows=1 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING note-wrong-deletion-round late line 2: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: deletion round 78 differs from subject round 79
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: missing 1
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

### M4

Selftest exit 0; fixture exit 1.

```text
APPEND_DEBT_SELFTEST pass=31 fail=0
```

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=1 bad_rows=1 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING note-wrong-deletion-round late line 2: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: deletion round 78 differs from subject round 79
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

### M5

Selftest exit 1; fixture exit 1.

```text
APPEND_DEBT_SELFTEST_FAIL honest exit=1 want=0 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL same-round exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL same-commit exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL out-of-population exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 2, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'note-wrong-deletion-round', 'detail': 'late line 2: cccccccccccccccccccccccccccccccccccccccc LOG.md 1111111111111111111111111111111111111111111111111111111111111111: deletion round 80 differs from subject round None'}]
APPEND_DEBT_SELFTEST_FAIL out-only exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: cccccccccccccccccccccccccccccccccccccccc LOG.md 1111111111111111111111111111111111111111111111111111111111111111: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL reverse-round exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL row-intro-later exit=1 want=0 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL row-intro-earlier exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL row-intro-unbound exit=1 want=1 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL note-subject-unresolvable exit=1 want=0 summary={'events': 2, 'accepted': 1, 'late': 0, 'pending': 1, 'unaccepted': 1, 'bad_rows': 1, 'bad_declarations': 0, 'out_of_population': 0} findings=[{'class': 'note-wrong-deletion-round', 'detail': 'late line 2: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: deletion round 80 differs from subject round None'}, {'class': 'count-short', 'detail': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb SCORECARD.md 2222222222222222222222222222222222222222222222222222222222222222: missing 1'}]
APPEND_DEBT_SELFTEST_FAIL late-path-bound exit=1 want=0 summary={'unaccepted': 1, 'bad_rows': 0, 'bad_declarations': 0, 'out_of_population': 0} findings=[]
APPEND_DEBT_SELFTEST pass=20 fail=11
```

```text
APPEND_DEBT round=84 base=aca4f33ac1e2 events=76 accepted=53 late=22 pending=0 unaccepted=2 bad_rows=1 bad_declarations=0 out_of_population=0
APPEND_DEBT_FINDING note-wrong-deletion-round late line 2: 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: deletion round 78 differs from subject round 79
APPEND_DEBT_FINDING count-short 1cda04569f30005adc89f98aa02909d6659fdf99 SCORECARD.md 86188047b683f9e78de1431aa98e18a71cb70e2ff512f4b294a45044e5bfb06e: missing 1
APPEND_DEBT_FINDING count-short 96e28374593be13833aebeb70150877f58f4aadc SCORECARD.md b2d76c4c24253879407fa21b658c339d75665e729ecb2469ab4c952a98579b21: missing 1
```

## Restoration and bounded commands

Each retained `M1.py`…`M5.py` is the actual mutated source. In scratch every mutant was restored to the pristine spec bytes before repeating BOTH identical commands. All five restored selftests exit 0 (pass=31 fail=0); every restored fixture exits 1 and its stdout is byte-identical to baseline. `hashes.json` records before/mutated/restored SHA-256; `restoration.json` additionally records restoration of the original HEAD tool bytes.

Commands were `python3 <scratch>/<name>.py --selftest` and `python3 <scratch>/<name>.py --repo . --round 84 --late .ufo/waves/round-84/fixtures/late-wrong-subject.tsv`, cwd `<scratch>/wt`, TMPDIR `<scratch>/tmp`, 350-second process deadline. Exact argv, stdout, stderr, duration and exit are retained in `commands.json` and each per-run JSON. All stderr was empty. No timeouts occurred.

Other shell commands: lane `rev-parse master` exit 0; lane `log --oneline -3` exit 0; fixture/output `ls` calls exit 0; `mkdir -p <scratch> <out> && git clone --shared <lane> <scratch>/wt` exit 0; read-only `git -C <scratch>/wt show HEAD:tools/round81-append-debt.py` exit 0. No local commits were needed. All file reads/globs/edits/writes completed successfully.

## Coverage findings (not implementation changes)

Add a matching known-subject positive control to distinguish subject vs accepting (M2); add deletion > subject mismatch (M3); assert the wrong row remains uncovered and exact summary counts (M4). Keep None-subject acceptance separately (M5). These are findings against the fallback spec harness, not claims about an unseen replacement.

## Self-evaluation

Accuracy 4/5: exact receipts retained; actual replacement unavailable. Completeness 4/5: all five probes and restores run; fallback cannot grade the eventual replacement. Clarity 4/5: killed-by-arm distinction explicit; full M5 failure output is lengthy. Actionability 4/5: each escape maps to a precise missing assertion; integration owner must evaluate delivery. Conciseness 4/5: exhaustive command receipts live separately. Overall 4.0. User agreement expected because limitations and survivors are explicit.

Cleanup: EXIT trap registered (exit 0), but persistent shell had not exited, so scratch still existed. Explicit `rm -rf -- /fast/scratch/hyaku/kama-r84/MT01Binding` then exited 0. Path absence observed: True; see `cleanup.json`.
