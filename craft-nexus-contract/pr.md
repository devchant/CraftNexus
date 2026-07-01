# Pull Request

## Summary
- Fix the stake-queue pruning logic so matured deposits are actually compacted and persisted back into indexed storage.
- Preserve the bounded queue semantics by removing matured entries and updating the stored count after pruning.
- Repair the active Rust build errors reported in tests and onboarding code so the contract compiles again.
- Add a regression test that verifies pruning leaves the latest deposit in storage and removes the expired entries.

## Changes
- Updated the stake queue pruning flow in [src/lib.rs](src/lib.rs) to ensure the compacted queue state is written back to persistent storage and the queue count is refreshed.
- Added the missing `ToString` import in [src/onboarding.rs](src/onboarding.rs) to resolve the `Symbol::to_string()` compile error.
- Fixed the event-access assertions in [src/test.rs](src/test.rs) to unwrap the event list correctly for the current Soroban event API.
- Fixed the moved-value issue in [src/expired_dispute_fee_test.rs](src/expired_dispute_fee_test.rs) by cloning the onboarding contract address before returning it from the test setup helper.
- Corrected the malformed onboarding test block in [src/onboarding_test.rs](src/onboarding_test.rs) so the suite compiles cleanly.
- Added/updated the pruning regression coverage in [src/scalability_test.rs](src/scalability_test.rs) and its snapshot [test_snapshots/scalability_test/test_artisan_stake_queue_pruning.1.json](test_snapshots/scalability_test/test_artisan_stake_queue_pruning.1.json).

## Testing
- `cargo check --tests`
- `cargo test test_artisan_stake_queue_pruning -- --nocapture`
- `cargo test`

## Notes
- The wasm release build still hits a local toolchain/runtime issue in this environment (`no global memory allocator found but one is required`), which is separate from the contract logic and test fixes. The host-side checks above completed successfully.

## Closes
- Closes #632
