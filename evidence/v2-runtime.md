# WhoElects v2 runtime evidence

Verified 2026-10-17, Asia/Saigon. Network: GenLayer StudioNet.
Mode shown in the user's Studio screenshots: Normal (Full Consensus), simulation off.

Contract: [0x5087c4bd62554051A832d849656880213f60a098](https://explorer-studio.genlayer.com/address/0x5087c4bd62554051A832d849656880213f60a098)

## Source identity

SHA-256 of contract source: `697e7beeabf65f1798800735e97e8d0a9cc9aee849989cf33c77f507f56c6a98`.

Three byte-identical copies were compared: the supplied v2 source, GitHub raw source,
and the deployed contract code returned in the explorer address page's deploy data.
GitHub commit observed at verification: [`e10edfab69fa0bf43e0ebae044c1e685bec80b9a`](https://github.com/nikvn89/WhoElects/tree/e10edfab69fa0bf43e0ebae044c1e685bec80b9a).
The commit deletes the obsolete root RUNTIME_EVIDENCE.md; it does not modify the contract.
[Contract source at that commit](https://github.com/nikvn89/WhoElects/blob/e10edfab69fa0bf43e0ebae044c1e685bec80b9a/contracts/WhoElects.py).
Uploading these documentation updates will create another commit; pin that new
submitted commit for final evidence. The contract hash remains the identity check.
A final-reviewed BASE commit has not been independently established; no comparison
URL is asserted to be the steward's reviewed baseline.

## Wallets actually used

| Role | Address |
|---|---|
| Author | `0x6276095FAEA15108740445ff277fdA8c304657F4` |
| Receiver / Customer | `0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277` |
| Outsider | `0x0a9Fa0b9a0B42981e43A8fb9A1D710E48cc7e095` |

These match decoded transaction senders on explorer. The receiver is the third
wallet supplied by the user, not the earlier historical v1 receiver.

## Evidence method

All 11 transactions below were independently retrieved from the public explorer
address page. The serialized method/arguments, sender, leader execution result and
semantic output were decoded. All 11 statuses were FINALIZED at retrieval. The
five successful transactions include deployment; the six rollbacks are expected
negative tests. A FINALIZED rollback is a passing rejection test, not a successful
state-changing operation. State readbacks below were checked in the supplied
Studio screenshots in Accepted state; these view values were not independently
queried via RPC. No new transactions were sent by the reviewer.

## Exact calls and results

### 0. Deploy

- Transaction: [0x7f637818ff9c9bd0b6e78737300eb4551bab65ab5c5109030c606f9955d836c2](https://explorer-studio.genlayer.com/tx/0x7f637818ff9c9bd0b6e78737300eb4551bab65ab5c5109030c606f9955d836c2)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Constructor: no arguments.
- Execution: **SUCCESS**. Result: `null`.
- Assessment: **PASS** for the stated case.

### 1. Open author option

- Transaction: [0x847c82b9ae95bf408ccbb58e8ded7e7cf4ed1c91267a649a90e402b9fa3c732f](https://explorer-studio.genlayer.com/tx/0x847c82b9ae95bf408ccbb58e8ded7e7cf4ed1c91267a649a90e402b9fa3c732f)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277",
    "Customer",
    "I choose either red or blue.",
    "red",
    "blue"
  ],
  "method": "open_option"
}
```

- Execution: **SUCCESS**. Result: `bf187b3fa53fff99ec812ded21b428adf4edcae9515c8c5d3b573f33327a04b9`.
- Semantic output: `{"outcome": "PERFORMER_CHOOSES"}`.
- Assessment: **PASS** for the stated case.

### 2. Author attempts third course

- Transaction: [0x1f086ff90094d49906ffafd35281e51ae833b6aaa46b348fc5c3e00d0e5cc7d3](https://explorer-studio.genlayer.com/tx/0x1f086ff90094d49906ffafd35281e51ae833b6aaa46b348fc5c3e00d0e5cc7d3)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "bf187b3fa53fff99ec812ded21b428adf4edcae9515c8c5d3b573f33327a04b9",
    "green"
  ],
  "method": "elect"
}
```

- Execution: **ROLLBACK**. Result: `Choose one of the two stored courses`.
- Assessment: **PASS** for the stated case.

### 3. Outsider attempts election

- Transaction: [0x4c52dae4e8bfce62d2a963a6d3fd88188c6a01119ecfd89f457ceda814061297](https://explorer-studio.genlayer.com/tx/0x4c52dae4e8bfce62d2a963a6d3fd88188c6a01119ecfd89f457ceda814061297)
- Sender: Outsider (`0x0a9Fa0b9a0B42981e43A8fb9A1D710E48cc7e095`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "bf187b3fa53fff99ec812ded21b428adf4edcae9515c8c5d3b573f33327a04b9",
    "red"
  ],
  "method": "elect"
}
```

- Execution: **ROLLBACK**. Result: `The choice here is not yours to make`.
- Assessment: **PASS** for the stated case.

### 4. Author elects stored course

- Transaction: [0x2faa171af78f654431c79bc9ef963d71de3175d3d9daaedd2cb6972902bda517](https://explorer-studio.genlayer.com/tx/0x2faa171af78f654431c79bc9ef963d71de3175d3d9daaedd2cb6972902bda517)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "bf187b3fa53fff99ec812ded21b428adf4edcae9515c8c5d3b573f33327a04b9",
    "blue"
  ],
  "method": "elect"
}
```

- Execution: **SUCCESS**. Result: `null`.
- Assessment: **PASS** for the stated case.

### 5. Open receiver option

- Transaction: [0xbb5877327f88618ba34f5c3b4e7741cb0dac8810054c66bde5d1689f283baa88](https://explorer-studio.genlayer.com/tx/0xbb5877327f88618ba34f5c3b4e7741cb0dac8810054c66bde5d1689f283baa88)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277",
    "Customer",
    "Customer chooses whether I deliver red or blue.",
    "red",
    "blue"
  ],
  "method": "open_option"
}
```

- Execution: **SUCCESS**. Result: `fcb1ce4c7e65a9332f813a95f33de12c9c8657cdfc6868f38138f646deaa5010`.
- Semantic output: `{"outcome": "RECEIVER_CHOOSES"}`.
- Assessment: **PASS** for the stated case.

### 6. Author attempts receiver election

- Transaction: [0x7159a2fbebf2910bf597a2485c98de1a364d5790f179fd864ad1b81470b35417](https://explorer-studio.genlayer.com/tx/0x7159a2fbebf2910bf597a2485c98de1a364d5790f179fd864ad1b81470b35417)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "fcb1ce4c7e65a9332f813a95f33de12c9c8657cdfc6868f38138f646deaa5010",
    "red"
  ],
  "method": "elect"
}
```

- Execution: **ROLLBACK**. Result: `The choice here is not yours to make`.
- Assessment: **PASS** for the stated case.

### 7. Receiver attempts third course

- Transaction: [0xcd0885eddd0f523306e714a3e67dc8e62d3ef03e55f6f95c0c78e25bb2c975e1](https://explorer-studio.genlayer.com/tx/0xcd0885eddd0f523306e714a3e67dc8e62d3ef03e55f6f95c0c78e25bb2c975e1)
- Sender: Receiver (`0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "fcb1ce4c7e65a9332f813a95f33de12c9c8657cdfc6868f38138f646deaa5010",
    "green"
  ],
  "method": "elect"
}
```

- Execution: **ROLLBACK**. Result: `Choose one of the two stored courses`.
- Assessment: **PASS** for the stated case.

### 8. Receiver elects stored course

- Transaction: [0x49a369b9391c5d705979d746d8f2537cfa18521dc21d6ad978105bad76cb813c](https://explorer-studio.genlayer.com/tx/0x49a369b9391c5d705979d746d8f2537cfa18521dc21d6ad978105bad76cb813c)
- Sender: Receiver (`0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "fcb1ce4c7e65a9332f813a95f33de12c9c8657cdfc6868f38138f646deaa5010",
    "red"
  ],
  "method": "elect"
}
```

- Execution: **SUCCESS**. Result: `null`.
- Assessment: **PASS** for the stated case.

### 9. Mismatched text/pair

- Transaction: [0xc3370c331aadbb61c235699dd771b5d97f7b1c59fb306e669c8f752f11e7d32d](https://explorer-studio.genlayer.com/tx/0xc3370c331aadbb61c235699dd771b5d97f7b1c59fb306e669c8f752f11e7d32d)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277",
    "Customer",
    "I choose either red or blue.",
    "train",
    "plane"
  ],
  "method": "open_option"
}
```

- Execution: **ROLLBACK**. Result: `Opening inconclusive; no option created`.
- Semantic output: `{"outcome": "INCONCLUSIVE"}`.
- Assessment: **PASS** for the stated case.

### 10. Unspecified chooser

- Transaction: [0x67c3313296f42b88f32cecdd33217ed1b8a667939c88311f25c805a866269178](https://explorer-studio.genlayer.com/tx/0x67c3313296f42b88f32cecdd33217ed1b8a667939c88311f25c805a866269178)
- Sender: Author (`0x6276095FAEA15108740445ff277fdA8c304657F4`). Status: **FINALIZED**.
- Exact decoded call:

```json
{
  "args": [
    "0x7Bbe56e52e810963e39Fd1cC166BF8CD192BB277",
    "Customer",
    "Red or blue is available.",
    "red",
    "blue"
  ],
  "method": "open_option"
}
```

- Execution: **ROLLBACK**. Result: `Opening inconclusive; no option created`.
- Semantic output: `{"outcome": "INCONCLUSIVE"}`.
- Assessment: **PASS** for the stated case.

## State readback observed in Studio screenshots

| Screenshot time, 2026-10-17 | Read | Observed |
|---|---|---|
| 18:19:02 | get_limits | WhoElects 2.0.0; courses_immutable=true; REVERT_WITHOUT_RECORD |
| 19:39:29 | First option after green rejection | OPEN; courses red/blue; chosen_course/elected_by empty |
| 19:40:41 | First option after outsider rejection | OPEN; courses red/blue; chosen_course/elected_by empty |
| 19:41:41 | First option after author elects blue | ELECTED; chosen_course=blue; elected_by author; courses red/blue |
| 19:43:02 | Second option after opening | OPEN; RECEIVER_CHOOSES; holder RECEIVER; elector receiver; courses red/blue |
| 19:46:37 | Second option after rejected elections | OPEN; chosen_course/elected_by empty; courses red/blue |
| 19:47:31 | Second option after receiver elects red | ELECTED; chosen_course=red; elected_by receiver; courses red/blue |
| 19:50:50 | Mismatched text/pair candidate | {} (no record) |
| 19:54:37 | Unspecified chooser candidate | {} (no record) |

Option IDs:

- First: `bf187b3fa53fff99ec812ded21b428adf4edcae9515c8c5d3b573f33327a04b9`.
- Second: `fcb1ce4c7e65a9332f813a95f33de12c9c8657cdfc6868f38138f646deaa5010`.
- Mismatched candidate: `ea8c244d6e6705bacacc77f123e2f5ee58f24aeee94825c22029065ad7c16733`.
- Unspecified chooser candidate: `f04aac4378b58025901e6397c1cb87e4d4dc398b68ae699ef221c8be6974f3cd`.

## What remains outside these observations

No live fault injection for provider outages/malformed output; those paths were
unit-tested with mocks. Objection, withdrawal, repeated election, input limits
and other deterministic edge cases were tested locally, not repeated in this live
run. Four semantic inputs passing here do not establish general semantic accuracy,
prompt-injection immunity or unanimous validator agreement. The first opening's
screenshot includes validator disagreement; final consensus still accepted the
PERFORMER_CHOOSES result. Historical v1 G4 failure remains preserved in
[v1-runtime.md](v1-runtime.md) and is not converted into a v2 pass.
