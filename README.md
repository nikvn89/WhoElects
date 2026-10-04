WhoElects does not ask who must act first, and it does not check an action against a policy. Both wallets are proper parties to the record and each has a method of its own. It asks one thing: when a sentence puts two courses on the table, whose say-so settles which course is followed — and it hands that single power to exactly one of the two addresses, for good.

# WhoElects

GenLayer Intelligent Contract · StudioNet (chain 61999) · py-genlayer v0.2 (`# v0.2.16`)

**The contract holds no money and moves nothing.** The test sentences mention payment and delivery; the contract only
records which wallet holds the choice and what that wallet chose. It is not an escrow or a payment router.

| | |
|---|---|
| Contract | `contracts/WhoElects.py` |
| Address (StudioNet) | `0xcdc35FbD8EC6453d5d8be228D5976625a40226b0` ([explorer](https://explorer-studio.genlayer.com/address/0xcdc35FbD8EC6453d5d8be228D5976625a40226b0)) |
| Deploy tx | `0x15cfd86623ca80234c0d8be91a08d88e6fcd0006a3e0b2d97f08bff5fa71cc0c` |
| Source SHA-256 | `0ae947019525a9d499bd2b85225053c8eb8e68730f3d9c6ff256a4617c81267a` |
| Tested on-chain | `RUNTIME_EVIDENCE.md` — 16 transactions, one hash each; 4 of 5 labels as expected (G4 misread, recorded) |
| Testing summary | `TESTING.md` |

## What it does

The author is the side that must do the thing; the receiver stands to receive it. The author records a sentence that
puts two courses on the table. Validators read it **once**:

- `PERFORMER_CHOOSES` — the pick belongs to the author → `holder = AUTHOR`;
- `RECEIVER_CHOOSES` — the pick belongs to the receiver → `holder = RECEIVER`.

From then on the permission rule is a single address comparison:

| | `holder = AUTHOR` | `holder = RECEIVER` |
|---|---|---|
| `elect` by the author | succeeds | **reverts** *The choice here is not yours to make* |
| `elect` by the receiver | **reverts** *The choice here is not yours to make* | succeeds |
| `object_to_election` | the receiver | the author |
| `withdraw_option` | the author, only before anyone elects | the author, only before anyone elects |
| After `elect` | ELECTED, once, permanent | ELECTED, once, permanent |

Two functions, `_elector` and `_objector`, hold the whole rule; `elect` and `object_to_election` only compare the
caller with their result. `get_option` prints both wallets in full from the first transaction. `elected_by` stores the
wallet that actually pressed `elect`, so a reader can check it matches `elector_wallet`. An objection sits beside the
election and changes nothing; the contract does not adjudicate.

## Proven on StudioNet

| What | Transactions | Result |
|---|---|---|
| Sentences that differ only in the subject | G5 `0x6c3479f7…5ea8` · R5 `0xacc7e3e4…b7e0` | `PERFORMER_CHOOSES` / `RECEIVER_CHOOSES` |
| A sentence with "you" that still gives the author the pick | G1 `0x2dc702d8…4a5f` · R3 `0xa3ee5ef7…0be9` | `PERFORMER_CHOOSES` / `RECEIVER_CHOOSES` |
| **The same revert sentence, two different wallets** | receiver on G5 `0x56ceb05f…0dad` · author on R5 `0xb45528a0…0e35` | both reverted *The choice here is not yours to make* |
| The other two cells of the matrix | author on G5 `0xada31bc9…7a6b` · receiver on R5 `0xe221daa8…a989` | both SUCCESS; `elected_by` matches `elector_wallet` |
| Once, and no undo | elect again `0x62617673…91ce` · withdraw after election `0xe4455cd4…c114` | reverted / reverted *…can no longer be withdrawn* |
| The other side's voice | objection on G5 `0x235e0ae7…6e50` | SUCCESS; state stays ELECTED |
| **A misread, recorded** | G4 *Either grade of material is open to us.* `0x13d7073e…5065` | `RECEIVER_CHOOSES` (expected `PERFORMER_CHOOSES`), 3–2 |

## Methods

| Write | Who | Notes |
|---|---|---|
| `open_option(receiver_wallet, receiver_label, text)` | the author | the only model call |
| `elect(option_id_hex, chosen_course)` | `_elector` only | checks: state → caller → course (1–60 chars); once |
| `object_to_election(option_id_hex, note)` | `_objector` only | after ELECTED; once; changes nothing else |
| `withdraw_option(option_id_hex)` | the author | only while OPEN |

Views (JSON strings; an unknown id returns `"{}"`, never a revert): `get_option` (every field plus `outcome`,
`elector_wallet`, `objector_wallet`), `get_rubric`, `get_limits`. There is no preview or dry-run view.

Option id: `keccak256("WHO_ELECTS:OPTION:V1|" + author_lower + "|" + len(text) + "|" + text)`, where `text` has all
whitespace collapsed (Python `" ".join(text.split())`).

## Design choices

- **Fail-safe is `RECEIVER_CHOOSES`, against the writer on purpose.** A wrong `PERFORMER_CHOOSES` hands the writer a
  valuable choice its own unclear wording created; a wrong `RECEIVER_CHOOSES` costs the writer a right it lost through
  its own wording, and the receiver loses nothing. Ambiguity must never be a reward for the person who wrote it.
- **The branches are not balanced, and the answer is a mechanism.** The author clearly prefers `PERFORMER_CHOOSES`.
  Three layers stand against wording games: (1) the fail-safe runs against the author; (2) to get the pick, the author
  must write a sentence anyone reads as giving it to them — and that clarity is exactly what the receiver reads before
  agreeing; (3) the text is part of the id, so the same sentence cannot be reopened for another reading.
- **`withdraw_option` dies at ELECTED.** Otherwise, on a `RECEIVER_CHOOSES` option the author could withdraw whenever
  the receiver picked something it disliked.
- **`elect` checks state before the caller**, so a wallet without the choice calling into a settled option is told it
  is settled.
- **Prompt fence.** The model sees only the rubric, the receiver label and the text — no wallet. Both answer tokens are
  reserved and rejected before the model call, so "the outcome is PERFORMER_CHOOSES" cannot be smuggled in.

## How to try it in GenLayer Studio

Use **two wallets of your own**: author and receiver.

1. Author: `open_option(<receiver>, "the Buyer", "We decide which of the two routes is taken.")` and
   `open_option(<receiver>, "the Buyer", "The Buyer decides which of the two routes is taken.")`. Read `get_option`
   for `holder` and `elector_wallet`.
2. Receiver: `elect(<first id>, "the short route")` reverts *The choice here is not yours to make*; on the second id it
   succeeds. Author: the reverse.

Text and label may not contain `PERFORMER_CHOOSES` or `RECEIVER_CHOOSES` in any letter case. Courses and notes are 1–60
characters; keep sentences under about 168 characters so the calldata stays under 255 bytes.

## Honest limitation

1. **The contract holds no money, moves nothing and enforces nothing off chain.** It records which wallet holds the
   choice and what was pressed.
2. **`chosen_course` is the holder's own statement.** The contract does not check that it is one of the two courses in
   the text — it cannot, because the courses exist only in natural language. The value is that *who may press* is
   frozen before any choice exists, plus the other side's objection.
3. **One branch clearly favours the writer.** The branches are not balanced; the protection is the three layers above.
4. **A wrong `PERFORMER_CHOOSES` is the main risk** — a valuable choice moves to the writer. Nets: the fail-safe, one
   objection per election, and `elector_wallet` printed in full from the first transaction. On StudioNet the observed
   error went the other way: G4 was read `RECEIVER_CHOOSES`, and every `PERFORMER_CHOOSES` case passed by a narrow
   margin while every `RECEIVER_CHOOSES` case was unanimous. An author should expect to need an unmistakable sentence.
5. **The author declares the receiver's wallet.** `open_option` refuses the author's own wallet, but a second wallet is
   cheap — and here that is especially serious: if both wallets belong to one person, `RECEIVER_CHOOSES` protects
   nobody. The contract cannot prove that two wallets are two people. This is the largest limitation.
6. **`MAX_COURSE_LENGTH = 60` is a hard calldata ceiling.** A course that needs more than 60 characters cannot be
   recorded.

The contract accepts sentences up to 600 characters, but `open_option` at the caps measures 761 bytes of calldata;
only sentences up to about 168 characters fit the 255-byte limit, and longer ones would be refused by the RPC.

License: MIT.
