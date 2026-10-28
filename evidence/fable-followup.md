# Fable feedback verification

Concern: remote send succeeds, then local delivered persistence fails, causing a duplicate after restart.

Result: not reproduced in the current single-runner implementation. Before send, uncertain is committed in a separate transaction. The final write failure leaves that prior state intact. No production logic change was needed.

Added tests:
- SQLite trigger aborts only the delivered update after a fake successful send. Close/reopen DB; assert one uncertain entry, zero pending entries, no repeat send, and actual runner refusal before any network call.
- Child process exits abruptly after recording fake remote acceptance. Reopen SQLite and assert uncertain state and no automatic resend.

All 17 tests pass. No live Telegram calls, credential reads or permission changes. Existing local architecture/acceptance documents were available; no separate Cursor TODO/spec file was present in this task workspace. This test does not establish power-loss durability or multi-runner correctness.
