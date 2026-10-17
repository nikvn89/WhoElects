# WhoElects v2 testing

Local run: 2026-10-17. Source: SHA-256 in README.

## Executed locally

**50 passed**: 44 contract tests and 6 serialized-calldata cases. GenLayer Direct
Mode uses the real v0.2.16 Python SDK/storage with mocked model outputs. It does
not run distributed consensus, live providers, wallet signatures or finality.
AST lint: passed, 3 checks. SDK validation and ABI schema extraction: passed
(7 methods: 3 view, 4 write; empty constructor). Dependencies are pinned in requirements-test.txt.
The old README's 46-test / 12-mutation counts are not reused as v2 evidence.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m pytest tests -q -p no:cacheprovider
genvm-lint lint contracts/WhoElects.py
```

The first Direct Mode run downloads the SDK. No private key or funded wallet is
needed. The two test files are included, so results can be reproduced.

Coverage includes both holder outcomes and both stored alternatives; third-course
and changed-string rejection with byte-identical post-state; unauthorized caller;
one-shot election; objection permissions and immutability; withdrawal terminality;
empty/duplicate courses; reserved tokens; UTF-8 limits; all-input ID binding;
unknown IDs; exact prompt/storage pair; canonical output parsing; provider error
rollback; retry after inconclusive opening; validator disagreement; calldata size.
Mocked mismatch/uncertainty tests validate handling of that result, **not whether a
real model will correctly recognize a mismatch**.

## V2 live status

**Critical live cases PASS**, based on user-executed Studio transactions on
2026-10-17 and independent explorer receipt/source verification.

Deployment: [0x5087c4bd62554051A832d849656880213f60a098](https://explorer-studio.genlayer.com/address/0x5087c4bd62554051A832d849656880213f60a098).
[Exact inputs, transaction links, source comparison and readbacks](evidence/v2-runtime.md).
All 11 transactions were FINALIZED when checked: 5 SUCCESS including deployment,
6 expected ROLLBACK. State readbacks are from the user's Accepted-state screenshots.

| Critical case | Observed |
|---|---|
| Author holds red/blue choice | PERFORMER_CHOOSES / AUTHOR |
| Author elects green | Membership rollback; remains OPEN |
| Outsider elects red | Authorization rollback; remains OPEN |
| Author elects blue | ELECTED / blue / elected_by author |
| Receiver holds red/blue choice | RECEIVER_CHOOSES / RECEIVER |
| Author elects on receiver option | Authorization rollback |
| Receiver elects green | Membership rollback; remains OPEN |
| Receiver elects red | ELECTED / red / elected_by receiver |
| Text red/blue, declared train/plane | INCONCLUSIVE rollback; no record |
| Red/blue text does not name chooser | INCONCLUSIVE rollback; no record |

The preserved evidence/v1-runtime.md is historical v1 data, including the G4 failure.
Live provider faults, malformed-output injection, objection/withdrawal and other
edge cases are NOT RUN in this v2 live session; related deterministic checks are
covered locally. No local suite was rerun solely for these documentation edits.

## Reproduction instructions for the tested critical cases

Use two different wallets A (author) and B (receiver). No constructor arguments.
Check `get_limits` → 2.0.0, immutable courses, INCONCLUSIVE rollback policy.
Use Normal (Full Consensus); inspect accepted state and transaction execution.

### 1. Author holds the choice and cannot select a third course

With A, call `open_option` with these five fields in order:

| Field | Value |
|---|---|
| receiver_wallet | B's full address |
| receiver_label | `Customer` |
| text | `I choose either red or blue.` |
| course_a | `red` |
| course_b | `blue` |

Save returned option ID as O1. `get_option(O1)` should show OPEN,
PERFORMER_CHOOSES, AUTHOR, course_a red, course_b blue.
With A, call `elect(O1, "green")`: expected rollback
`Choose one of the two stored courses`. Read O1 again: it must be unchanged.
With a third-party wallet C, call `elect(O1, "red")`: expected authorization rollback, unchanged.
With A, call `elect(O1, "blue")`: expected ELECTED, chosen_course blue,
elected_by A; original course pair unchanged.

### 2. Receiver holds the choice

With A, open a second option with the same wallet/label/courses but text:
`Customer chooses whether I deliver red or blue.`
Save returned ID as O2. Expected RECEIVER_CHOOSES and RECEIVER.
With A, `elect(O2, "red")` must revert for authorization.
With B, `elect(O2, "green")` must revert for course membership.
With B, `elect(O2, "red")` should succeed, elected_by B, courses unchanged.
If a real outcome differs, record the failure; do not overwrite the expected label.

### 3. Semantic binding and ambiguity

With A, try `open_option(B, "Customer", "I choose either red or blue.",
"train", "plane")`. Expected inconclusive rollback: no record and no holder.
Then try `open_option(B, "Customer", "Red or blue is available.", "red", "blue")`.
Expected inconclusive rollback because no chooser is stated. These two cases
must use the real model; local mocks do not prove them. A success here is a
semantic failure to investigate before claiming the fix complete.

Provider failures and malformed model outputs were tested locally. Live injection
of those faults is NOT RUN; do not add an administrative backdoor to simulate it.
Other deterministic guards are covered locally; no need to repeat every unit case
manually unless Studio behavior differs.

## Submission evidence

Actual v2 results are in [evidence/v2-runtime.md](evidence/v2-runtime.md).
Retain the deployed contract and source hash. After uploading the documentation
update, pin the new submitted GitHub commit. The source-observed commit recorded
in the runtime report predates only this documentation update. If a compare URL
is requested, establish the final-reviewed BASE separately; do not invent it.
