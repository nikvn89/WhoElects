# WhoElects v2.0.0

WhoElects records who may choose between **two explicit, immutable courses**.
GenLayer validators read the supplied text and that exact pair once per opening
attempt. They determine whether the author (performer) or the named receiver
holds the choice. Only that wallet can elect one of the stored courses, once.

## Correction from v1

The reviewed v1 checked the caller but accepted any nonempty course string.
V2 stores `course_a` and `course_b` when the option is opened, exposes both in
`get_option`, and rejects any election outside that pair before writing state.
There is no method to edit either course. The classifier sees exactly the same
validated courses that are stored. The ID binds the author, receiver wallet,
receiver label, option text and ordered pair.

The classifier also checks whether the text actually offers that pair. Unclear
pair binding, unclear chooser, malformed output or catchable provider failure
must not assign a holder: `INCONCLUSIVE` rolls back the opening, leaving no record.
This replaces v1's automatic receiver assignment on uncertainty. Independent
validators rerun the evaluation and require the same canonical result.

## State and permissions

| Operation | Caller | Result |
|---|---|---|
| `open_option` | Author, different from receiver | Definite outcome creates OPEN with frozen courses and holder; returns option ID |
| `elect` | Frozen holder only | OPEN → ELECTED, one stored course, irreversible |
| `object_to_election` | Other party only | One note after ELECTED; does not reverse the election |
| `withdraw_option` | Author only | OPEN → WITHDRAWN; cannot withdraw after election |

No money, external web, clock, owner override or administrative method is used.

## Deploy and call

Deploy **a new instance** of `contracts/WhoElects.py` in GenLayer Studio, Normal
(Full Consensus). Constructor: no arguments. Do not upgrade a v1 instance:
storage, opening arguments, IDs and semantic handling changed. `get_limits`
must report `version = 2.0.0` and `courses_immutable = true`.

```python
# Signed by author A; B is a DIFFERENT wallet controlled by the tester.
option_id = open_option(
    B, "Customer", "I choose either red or blue.", "red", "blue"
)
get_option(option_id)
elect(option_id, "green")  # holder: must revert, remains OPEN
elect(option_id, "blue")   # holder: succeeds, becomes ELECTED
```

Use the ID returned by the opening transaction, then read it with `get_option`
in Accepted state. A submitted transaction hash is not proof of success; inspect
execution result, consensus/finality and post-state. Studio/explorer may expose
the returned ID in the execution return value. The independent ID recipe is also
included in `tests/test_whoelects.py` (`option_id`) for reproducible calculation.

Public methods:

- `open_option(receiver_wallet, receiver_label, text, course_a, course_b) -> str`
- `elect(option_id_hex, chosen_course) -> None`
- `object_to_election(option_id_hex, note) -> None`
- `withdraw_option(option_id_hex) -> None`
- `get_option(option_id_hex) -> str` (JSON; unknown ID returns `{}`)
- `get_limits() -> str` (JSON), `get_rubric() -> str`

Courses are normalized by splitting and joining whitespace with one space.
They must be nonempty and differ after this normalization and lowercasing.
Election membership is **case-sensitive exact equality** after whitespace
normalization. Thus ` red ` selects stored `red`; `RED`, `red.` and `green` do
not. Synonyms, visually similar Unicode characters and semantic equivalence are
not accepted as substitutes by `elect`.

## Size limits

All lengths are UTF-8 bytes after validation/normalization:

| Field | Limit |
|---|---:|
| Text | 120 |
| Receiver label | 24 |
| Each course | 40 |
| Total label + text + both courses | 160 |
| Objection note | 60 |

Send canonical, trimmed positional arguments. Maximum-budget opening calldata
measured 238 bytes; `elect` 128; objection 162. These are encoded calldata sizes,
not the size of a signed transaction. Adding excess whitespace to raw requests or
using keyword arguments can enlarge payloads before the contract validates them.
The tests check the positional encoding and multibyte inputs.

## Tests and evidence

See [TESTING.md](TESTING.md). The supplied suite has **50 passing local tests**
using GenLayer SDK v0.2.16 Direct Mode and mocked model outputs, plus AST lint and SDK validation/schema extraction.
These establish deterministic guards/storage behavior, not real AI accuracy or
network consensus.

The v2 instance [0x5087c4bd62554051A832d849656880213f60a098](https://explorer-studio.genlayer.com/address/0x5087c4bd62554051A832d849656880213f60a098)
was deployed and tested on 2026-10-17. [V2 runtime evidence](evidence/v2-runtime.md)
records all 11 FINALIZED transactions (deployment plus 10 calls): both chooser
branches, rejection of third courses, permission checks, valid elections, pair
mismatch and unclear chooser. Source on explorer and GitHub matches the SHA below.
Execution receipts were independently decoded; state readbacks come from the user's
Studio screenshots. See that report for scope and remaining unrun live cases.

[Original v1 evidence](evidence/v1-runtime.md) is historical and retains its
recorded semantic failure. It does not validate v2. V2 results are recorded separately
in TESTING.md and evidence/v2-runtime.md; compare source SHA-256 below.
Pin repository source to the submitted commit SHA. If a compare link is requested,
use the actual final-reviewed BASE and submitted HEAD SHAs, not `main`.

## Limits of the claim

The code guarantees membership in the stored pair. Whether that pair matches the
natural-language text and who holds the choice remain probabilistic semantic
judgments. Prompt fencing and consensus do not prove immunity to prompt injection
or model errors. Different-looking phrases can describe the same real course;
only the model evaluates semantic distinctness. This is an onchain choice record,
not proof of identity, consent, performance, legal validity or real-world effects.
The author supplies the text, roles and alternatives without receiver approval.
Repeated openings with altered inputs are possible; no Sybil protection is claimed.

## Source integrity

Contract SHA-256: `697e7beeabf65f1798800735e97e8d0a9cc9aee849989cf33c77f507f56c6a98`

```bash
sha256sum contracts/WhoElects.py
# macOS: shasum -a 256 contracts/WhoElects.py
```
