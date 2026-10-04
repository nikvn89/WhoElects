# TESTING

```
COMPILE PASS ≠ RUNTIME PASS
SUBMITTED ≠ ACCEPTED ≠ FINALIZED ≠ EXECUTION SUCCESS ≠ POSTCONDITION PASS
```

## On-chain (GenLayer StudioNet, 2026-10-04)

Two wallets (author, receiver), every option opened with the label `the Buyer`, in GenLayer Studio (Normal / Full
Consensus). Full table with inputs, hashes, results and read-back state: `RUNTIME_EVIDENCE.md`.

| Check | Cases | Result |
|---|---|---|
| **Check 1** — sentences that differ only in the final pronoun (`us` / `you`) | G4 → expected `PERFORMER_CHOOSES`, got **`RECEIVER_CHOOSES`** (3–2); R4 not opened | **FAIL** |
| Check 1, second pair — sentences that differ only in the subject | G5 → `PERFORMER_CHOOSES`, R5 → `RECEIVER_CHOOSES` | PASS |
| **Check 2** — "you" in a sentence that still gives the author the pick | G1 → `PERFORMER_CHOOSES`, R3 → `RECEIVER_CHOOSES` | PASS |
| **Check 3** — the four-cell matrix (one method, two wallets, two options) | on G5: receiver reverts, author succeeds; on R5: author reverts, receiver succeeds | PASS |
| once only | a second `elect` reverts *already elected* | PASS |
| the other side's voice | `object_to_election` succeeds and changes nothing else | PASS |
| no undo after a choice | `withdraw_option` after ELECTED reverts | PASS |
| the WITHDRAWN exit | `withdraw_option` on an open option succeeds | PASS |
| only the author withdraws | a receiver call reverted (sent by mistake, kept as evidence) | PASS |

**Agreement margins.** G4 (misread) 3–2; G5 needed a leader rotation before it was accepted; G1 3–2. R5 and R3 were
both 3/3. Every `PERFORMER_CHOOSES` case was close and every `RECEIVER_CHOOSES` case unanimous: the rubric's
"where the text does not settle it, return RECEIVER_CHOOSES" pulls the model toward the receiver when a sentence
signals the author only through a pronoun. The rubric was not changed after the run.

Test cases (5 pairs, same surface, opposite labels):

| Case | Text | Expected | On-chain |
|---|---|---|---|
| G4 | Either grade of material is open to us. | PERFORMER_CHOOSES | **RECEIVER_CHOOSES** |
| R4 | Either grade of material is open to you. | RECEIVER_CHOOSES | not sent |
| G5 | We decide which of the two routes is taken. | PERFORMER_CHOOSES | PERFORMER_CHOOSES |
| R5 | The Buyer decides which of the two routes is taken. | RECEIVER_CHOOSES | RECEIVER_CHOOSES |
| G1 | We may deliver to you in one shipment or in several. | PERFORMER_CHOOSES | PERFORMER_CHOOSES |
| R3 | You may require the work on site or remotely. | RECEIVER_CHOOSES | RECEIVER_CHOOSES |
| G2 | Payment may be made by transfer or by card, as we find convenient. | PERFORMER_CHOOSES | not sent |
| R2 | Payment may be taken by transfer or by card, whichever the Buyer prefers. | RECEIVER_CHOOSES | not sent |
| G3 | The work may be carried out on site or remotely, at our option. | PERFORMER_CHOOSES | not sent |
| R1 | The Buyer may call for delivery in one shipment or in several. | RECEIVER_CHOOSES | not sent |

## Offline (before deploy)

- **genvm-linter** `lint`, `schema`, `typecheck`: pass; 7 methods (4 write, 3 view), no type errors.
- **Direct Mode tests** (`genlayer-test`, the real py-genlayer v0.2.16 SDK, model mocked): 46 passed — `_elector` and
  `_objector` for both holders and always different, the four-cell matrix, the runtime table replayed, state checked
  before the caller, all 22 revert strings each with a dedicated test, id formula and whitespace normalization,
  fail-safe, validator function, prompt fence, views. Twelve deliberate faults (the elector fixed to the author, the
  objector fixed, the caller check skipped, the check order reversed, withdraw allowed after election, `elected_by`
  forged, the holder fixed, the fail-safe flipped, an objection that reopens, a second objection allowed, an answer
  token removed from the fence, withdraw open to anyone) were each caught by a test.
- **Rubric gate**: no word or word pair separates the two test classes; the rubric shares no content word with any of
  the 10 cases and avoids *decide, prefer, option, require, call for*.
- **Calldata**: every call used on-chain is between 101 and 167 bytes, under the 255-byte RPC limit.

## Consensus behaviour

The model is called once, in `open_option`. Validators re-run the classification and must agree on the exact label;
a disagreement rotates the leader or reverts the transaction (fail-closed). Re-running does not defend against prompt
injection — the fence does.

## What this run does NOT prove

- One of the five labels sent was wrong (G4). Label stability is weak for sentences that name the author only through a
  pronoun; repeated runs and other validator sets were not measured.
- Five of the ten semantic cases were not sent.
- Sentences longer than about 168 characters (the contract allows 600) were not sent.
- Prompt-injection resistance rests on the fence and the reserved-token check; no adversarial model run was done.
