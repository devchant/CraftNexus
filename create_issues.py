#!/usr/bin/env python3
"""
CraftNexus Smart Contract - GitHub Issue Creator
=================================================
Creates 80 deeply researched GitHub issues for Hub-of-Evolution/CraftNexus

USAGE
-----
1. Set your GitHub Personal Access Token (classic, needs repo + issues:write scope):
       $env:GITHUB_TOKEN = "ghp_xxxxxxxxxxxx"   # PowerShell
   OR paste it when prompted.

2. Install requests if needed:
       pip install requests

3. Run:
       python create_issues.py
"""
import os, sys, time, requests

REPO_OWNER = "Hub-of-Evolution"
REPO_NAME  = "CraftNexus"
API_BASE   = "https://api.github.com"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
if not GITHUB_TOKEN:
    GITHUB_TOKEN = input("Paste your GitHub Personal Access Token: ").strip()

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

LABEL_COLORS = {
    "security":"d73a4a","bug":"fc2929","build":"e4e669",
    "performance":"0075ca","storage":"cfd3d7","testing":"a2eeef",
    "architecture":"7057ff","documentation":"0075ca","tooling":"e4e669",
    "enhancement":"84b6eb","escrow":"f9d0c4","onboarding":"bfd4f2",
    "migration":"d4c5f9","technical-debt":"e99695","refactoring":"fef2c0",
    "dead-code":"e0e0e0","ci":"0052cc",
}

PREREQ = (
    "\n---\n"
    "## CRITICAL PREREQUISITE - Fix Active Build Errors First\n\n"
    "Contributors MUST ensure `cargo check --tests` passes before submitting PRs.\n\n"
    "| Error | Location | Fix |\n"
    "|---|---|---|\n"
    "| E0609 no field on Option | src/test.rs lines 2559,2567,2584,2592,2601,2609 | Add `.unwrap()` before `.1`/`.2` |\n"
    "| E0599 no method to_string | src/onboarding.rs lines 2149,2255,3395 | Add `use crate::alloc::string::ToString;` |\n"
    "| E0382 moved value | src/expired_dispute_fee_test.rs:68 | Add `.clone()` before first move |\n"
    "| Unclosed delimiter | src/onboarding_test.rs:2157 | Add missing closing `}` |\n"
    "| Cannot find macro vec | src/min_release_window_test.rs:339,437 | Add `use soroban_sdk::vec;` |\n\n"
    "Verify with: `cargo check --tests && cargo test`\n"
)

CHECKLIST = (
    "\n---\n"
    "## Verification Checklist\n"
    "- [ ] `cargo check --tests` - zero errors\n"
    "- [ ] `cargo test` - all suites pass\n"
    "- [ ] `cargo build --target wasm32-unknown-unknown --release` succeeds\n"
    "- [ ] Snapshot files unchanged or updated intentionally\n"
    "- [ ] PR description references this issue number\n"
)

def make_body(ctx, impacts, actions):
    impact_rows = "\n".join(f"| {k} | {v} |" for k, v in impacts)
    action_lines = "\n".join(f"{i+1}. {a}" for i, a in enumerate(actions))
    return (
        f"## Context and Background\n\n{ctx}\n\n"
        f"## Impact and Severity\n\n| Field | Value |\n|---|---|\n{impact_rows}\n\n"
        f"## Proposed Action Items\n\n{action_lines}\n"
        + PREREQ + CHECKLIST
    )

# ---------------------------------------------------------------------------
# 80 Issues Definition
# ---------------------------------------------------------------------------
ISSUES = [

# ===== SECURITY (1-20) =====================================================

dict(title="[SECURITY] Audit and protect endpoint #57 (read_username_fee_token) against unauthorized invocation",
     labels=["security","onboarding"],
     body=make_body(
"`read_username_fee_token` at `src/onboarding.rs` line 955 reads "
"`DataKey::UsernameChangeFeeToken` and extends its TTL. Although an internal helper, "
"it is called from fee-collection paths that handle real token transfers. A caller who "
"can influence the returned token could redirect username-change fees to an attacker-"
"controlled address. This is part of the **stellar wave** codebase security sweep "
"targeting high-performance, safety, and reliability on the Stellar Soroban network. "
"The check-effects-interactions (CEI) pattern mandates external token transfers are the "
"very last step; a mutable fee-token pointer that can be changed mid-transaction is a "
"classic reentrancy surface.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","948-955"),("Impact Level","High - attacker could redirect fee payments")],
["Add an admin-only `require_auth()` guard to any public setter that writes `DataKey::UsernameChangeFeeToken`.",
 "Snapshot the fee-token address at the start of `change_username` and assert it has not changed before the transfer executes.",
 "Add a test verifying a concurrent setter cannot redirect the fee mid-call.",
 "Ensure CEI: **read** fee token -> **deduct** balance -> **transfer** last."])),

dict(title="[SECURITY] Enforce require_auth() on set_escrow_contract before storage mutation",
     labels=["security","onboarding"],
     body=make_body(
"`set_escrow_contract` at `src/onboarding.rs` line 2446 stores the address of the trusted "
"escrow contract. This address is used by `update_user_metrics` and `update_active_contracts` "
"to gate write access. If an attacker calls this function and substitutes their own contract "
"address, they gain unrestricted ability to falsify user metrics and verification data.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2446-2487"),("Impact Level","Critical - allows full metric manipulation")],
["Verify `config.platform_admin.require_auth()` is called **before** the storage write on line 2470.",
 "Add a `#[should_panic]` test that calls `set_escrow_contract` without mocked auth and asserts rollback.",
 "Add a positive test confirming admin auth succeeds and the address is persisted correctly.",
 "Extend the TTL of `DataKey::Config` after writing."])),

dict(title="[SECURITY] Protect set_verification_thresholds against non-admin mutation (Issue #422)",
     labels=["security","onboarding"],
     body=make_body(
"`set_verification_thresholds` at `src/onboarding.rs` line 2488 allows overriding "
"`min_escrow_count_for_verify` and `min_volume_for_verify`. A malicious caller who lowers "
"these thresholds to zero can auto-verify any artisan without completing real transactions, "
"bypassing the entire trust-building mechanism. PR #422 added the `require_auth()` guard - "
"this issue tracks a hardening audit to confirm there is no bypass path.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2488-2527"),("Impact Level","High - threshold bypass enables fraudulent verification")],
["Audit the call site: confirm `require_auth()` precedes the `env.storage()` write.",
 "Ensure the escrow-contract caller path cannot invoke this function.",
 "Add unauthorized-caller `#[should_panic]` tests covering zero-auth and non-admin callers.",
 "Document the admin-only restriction in the function doc-comment."])),

dict(title="[SECURITY] Validate batch-escrow buyer authentication for every buyer in batch (Issue #111)",
     labels=["security","escrow"],
     body=make_body(
"`create_batch_escrow` at `src/lib.rs` line 4835 performs a **single** `require_auth()` on "
"the first buyer (lines 4857-4858), then creates escrows for all subsequent buyers without "
"re-authenticating. A single authorized transaction can create escrows on behalf of buyers "
"who did not sign, locking their funds without consent.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","4835-4975"),("Impact Level","Critical - unauthorized fund lock-up")],
["Require `buyer.require_auth()` for **every** distinct buyer in the batch.",
 "Add a batch test with two different buyers and assert the transaction panics when the second buyer has not signed.",
 "Update the function doc-comment to clarify the authorization model.",
 "Consider restricting `create_batch_escrow` to single-buyer batches for auditability."])),

dict(title="[SECURITY] Reentrancy guard missing exit call on early-return paths in release_funds",
     labels=["security","escrow"],
     body=make_body(
"`release_funds` at `src/lib.rs` line 3451 calls `Self::enter_reentry_guard(&env)` at the "
"top. If any non-panicking early Err(...) return is introduced in the future, the guard will "
"remain set and permanently lock the contract. Soroban panics do roll back state (including "
"the guard), but this is a latent DoS risk if error handling patterns change in future refactors.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","3451-3547"),("Impact Level","Medium - latent DoS if error handling changes")],
["Audit every code path in `release_funds`, `auto_release`, `refund`, and `resolve_dispute` to confirm each Err(...) return is preceded by `Self::exit_reentry_guard(&env)`.",
 "Consider wrapping the guard in an RAII-style struct via a closure pattern for automatic exit.",
 "Add a `reentrancy_test` that simulates a failing mid-call and verifies the guard is cleared afterward."])),

dict(title="[SECURITY] Admin recovery window has no minimum floor - add time-lock validation",
     labels=["security","escrow"],
     body=make_body(
"`recover_admin_access` at `src/lib.rs` line 2444 allows a pre-registered recovery address "
"to claim admin rights. The cooldown window is not validated against a minimum floor, allowing "
"a deployer to set it to zero and bypass the time-lock entirely. On Stellar Soroban, admin "
"key compromise is catastrophic: the admin can whitelist tokens, change fees, and approve upgrades.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","2444-2517"),("Impact Level","High - trivial admin takeover with zero cooldown")],
["Define MIN_ADMIN_RECOVERY_COOLDOWN = 7 * 24 * 3600 seconds and enforce it in `recover_admin_access`.",
 "Add a test that attempts recovery with a zero-second window and asserts `Error::AdminRecoveryFailed`.",
 "Document the minimum cooldown in the function doc-comment and README."])),

dict(title="[SECURITY] WASM upgrade proposal lacks signer deduplication - replay votes possible",
     labels=["security","escrow"],
     body=make_body(
"`propose_upgrade_wasm` at `src/lib.rs` line 3736 allows any configured signer to vote for "
"a new WASM hash. There is no guard preventing the same address from approving the same hash "
"twice, inflating the approval count. A single compromised signer key could push through a "
"malicious upgrade alone, bypassing the multi-sig threshold.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","3736-3819"),("Impact Level","Critical - single-signer upgrade bypass")],
["Before appending to the approvals list, verify the signing address is not already present.",
 "Return Err(Error::AlreadyApproved) on duplicate votes.",
 "Add a test that has one signer vote twice and confirms the approval count remains at 1.",
 "Add a test that reaches the threshold only with the correct number of unique signers."])),

dict(title="[SECURITY] transfer_platform_fee called with out-of-scope config variable - silent fee routing failure",
     labels=["security","bug","escrow"],
     body=make_body(
"Archived compiler output records: error[E0425]: cannot find value 'config' in this scope "
"--> src/lib.rs:1606. The `config` variable is loaded in an outer scope and not captured in "
"the inner block calling `transfer_platform_fee`. This means platform fees may not be routed "
"to the correct wallet, resulting in a silent financial loss for the platform on every trade.",
[("Category","Security / Bug"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1600-1615, 2918-2928"),("Impact Level","High - fee routing failure")],
["Confirm whether both occurrences at lines 1606 and 2923 are still present in the current codebase.",
 "Load `config` within the same block that calls `transfer_platform_fee`, or pass it as a parameter.",
 "Add integration tests verifying platform fees arrive at the correct wallet address after `release_funds` and `resolve_dispute`."])),

dict(title="[SECURITY] Audit update_user_role for unauthorized role escalation to Admin (Endpoint #85)",
     labels=["security","onboarding"],
     body=make_body(
"`update_user_role` at `src/onboarding.rs` line 2063 (Endpoint #85) allows the platform admin "
"to assign any `UserRole`, including `Admin` itself. A single compromised admin account can create "
"additional admins via this function, enabling unlimited privilege escalation. The [SECURITY] "
"comment at line 2076 notes role-assignment validation must be explicit and tested.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2063-2140"),("Impact Level","High - admin privilege escalation")],
["Add an explicit guard: if new_role == UserRole::Admin, return an error or panic with a descriptive message.",
 "Add a `#[should_panic]` test that attempts to escalate a Buyer to Admin and asserts rollback.",
 "Update the doc-comment to document the restriction."])),

dict(title="[SECURITY] deactivate_profile does not validate active escrow obligations when escrow contract is unregistered",
     labels=["security","onboarding"],
     body=make_body(
"`deactivate_profile` at `src/onboarding.rs` line 2141 checks `active_contract_count`, "
"maintained by the escrow contract. If `config.escrow_contract == None`, the counter is never "
"incremented and a seller with open escrows can deactivate their profile mid-trade, leaving "
"buyers with no recourse and funds potentially locked.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2141-2238"),("Impact Level","High - buyer funds at risk")],
["When `config.escrow_contract` is None, add a secondary check before allowing deactivation.",
 "Add a test that attempts deactivation with an open escrow when no escrow contract is registered and asserts revert.",
 "Document the dependency on the escrow contract in the function doc-comment."])),

dict(title="[SECURITY] get_user_reputation exposes sensitive trade data without caller authorization (Issue #446)",
     labels=["security","onboarding"],
     body=make_body(
"`get_user_reputation` at `src/onboarding.rs` line 3257 returns a user's "
"(successful_trades, disputed_trades) tuple. Issue #446 in onboarding_test.rs line 2076 notes "
"this endpoint must reject callers without user authorization. Without require_auth(), any "
"anonymous contract call can harvest trade-dispute ratios for all users, enabling targeted "
"social engineering attacks against users with high dispute rates.",
[("Category","Security / Privacy"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","3257-3333"),("Impact Level","Medium - user privacy breach")],
["Add `address.require_auth()` at the start of `get_user_reputation`.",
 "Extend TTL of `DataKey::UserProfile(address)` after the auth check.",
 "Add an unauthorized-caller `#[should_panic]` test.",
 "Add an authorized-caller positive test confirming the correct tuple is returned."])),

dict(title="[SECURITY] Missing require_auth on get_user_metrics exposes trade activity data (Issue #430)",
     labels=["security","onboarding"],
     body=make_body(
"`get_user_metrics` at `src/onboarding.rs` line 2578 returns `UserMetrics { total_escrow_count, "
"total_volume }` for any address. Issue #430 (line 2047 of onboarding_test.rs) flags this endpoint "
"must reject unauthorized callers. Exposing exact trade volumes per user enables competitor "
"analysis and targeted price manipulation in the marketplace.",
[("Category","Security / Privacy"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2578-2640"),("Impact Level","Medium")],
["Confirm `address.require_auth()` is called before reading `DataKey::UserMetrics`.",
 "Add `#[should_panic]` test for unauthorized access.",
 "Add authorized-access positive test.",
 "Extend TTL after the auth-gated read."])),

dict(title="[SECURITY] get_verification_queue must enforce admin-only access (Issue #474, Endpoint #73)",
     labels=["security","onboarding"],
     body=make_body(
"`get_verification_queue` at `src/onboarding.rs` line 3137 returns the ordered list of pending "
"verification requests. The [SECURITY] comment at line 3144 documents admin-only restriction. "
"Any non-admin reading this list could selectively bribe administrators to approve or delay "
"specific users, compromising the integrity of the verification system.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","3137-3202"),("Impact Level","High")],
["Confirm `config.platform_admin.require_auth()` fires before iterating the queue.",
 "Add a test with a non-admin caller that asserts a panic/rollback.",
 "Add a positive test for admin access.",
 "Ensure the queue's TTL is extended on every admin read."])),

dict(title="[SECURITY] set_moderator must prevent non-onboarded addresses from being promoted (Issue #470)",
     labels=["security","onboarding"],
     body=make_body(
"`set_moderator` at `src/onboarding.rs` line 2021 (Endpoint #69) promotes a user to Moderator "
"sub-role. If the target address is not yet onboarded, the function creates an inconsistent state "
"where an unlinked address holds moderator privileges without a profile entry, breaking role "
"validation in all downstream calls.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2021-2062"),("Impact Level","High")],
["Add an explicit is_onboarded check before role assignment; panic with UserNotFound if the address lacks a profile.",
 "Add a `#[should_panic]` test for the unregistered-address path.",
 "Confirm the test snapshot `test_set_moderator_unknown_user_panics.1.json` covers this case."])),

dict(title="[SECURITY] extend_release_window cumulative cap not enforced - buyer can delay payment indefinitely",
     labels=["security","escrow"],
     body=make_body(
"`extend_release_window` at `src/lib.rs` line 3647 allows the buyer to extend the auto-release "
"deadline. The `MAX_RELEASE_WINDOW` constant is validated against the **original** window, not "
"the **cumulative** window after multiple extensions. A buyer can call this function repeatedly "
"to push the release date indefinitely, denying payment to sellers.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","3647-3735"),("Impact Level","High - seller payment denial")],
["Track a `total_extension_seconds` field or compute from `release_time - created_at`.",
 "Assert `total_extension_seconds <= MAX_RELEASE_WINDOW` after applying each new extension.",
 "Add a test that applies multiple extensions and asserts the cumulative cap is enforced."])),

dict(title="[SECURITY] propose_upgrade_wasm cooldown bypassed by cancel-and-reprpose pattern",
     labels=["security","escrow"],
     body=make_body(
"`cancel_upgrade_wasm` at `src/lib.rs` line 3942 clears the upgrade proposal and **resets the "
"cooldown**. An admin with a malicious WASM hash can cancel and immediately re-propose it, "
"resetting the waiting period and evading the time-lock designed to allow community review.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","3942-3970"),("Impact Level","High")],
["Record a `last_cancelled_at` ledger timestamp when a proposal is cancelled.",
 "In `propose_upgrade_wasm`, assert `env.ledger().timestamp() - last_cancelled_at >= UPGRADE_COOLDOWN_SECONDS`.",
 "Add a test that cancels and immediately re-proposes and asserts `Error::UpgradeCooldownActive`."])),

dict(title="[SECURITY] Artisan stake minimum bypassed with non-standard-decimal tokens (Issue #421)",
     labels=["security","escrow"],
     body=make_body(
"`unstake_tokens` validates the stake token matches original (PR #421). However, the minimum "
"stake check in `create_escrow` line 2569 reads `config.min_stake_required` without normalizing "
"for token decimals. A seller could stake a 0-decimal token where 1 unit = 1 stroop and satisfy "
"the minimum numerically while staking far less real value.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","2569-2640"),("Impact Level","Medium - stake requirement circumvention")],
["Normalize stake amounts to a canonical 7-decimal representation before comparing against `min_stake_required`.",
 "Add FeeTokenInfo.min_amount validation for stake tokens specifically.",
 "Add a test with a non-standard-decimal token and assert the minimum is correctly enforced."])),

dict(title="[SECURITY] Refund path must set state before token transfer to enforce strict CEI ordering",
     labels=["security","escrow"],
     body=make_body(
"`refund` in `src/lib.rs` validates escrow state but the state transition and token transfer must "
"follow strict CEI ordering. A sequence of calls across ledgers could result in double-refund if "
"the state is not set to `Refunded` atomically before the transfer. On Soroban each invocation is "
"atomic, but state must always be updated BEFORE external calls per CEI.",
[("Category","Security"),("Target File","`src/lib.rs`"),
 ("Specific Lines","refund function"),("Impact Level","Medium")],
["Confirm that state is set to `Refunded` **before** the token transfer (strict CEI ordering).",
 "Add a test that calls `refund` then `resolve_dispute` in sequence and asserts the second panics with `Error::InvalidEscrowState`.",
 "Review `reentrancy_test.rs` snapshot `test_refund_cei_pattern` to confirm existing coverage."])),

dict(title="[SECURITY] onboard_user allows registration while contract is paused - no pause-state check",
     labels=["security","onboarding"],
     body=make_body(
"`onboard_user` at `src/onboarding.rs` line 1572 (Endpoint #93) does not check whether the "
"escrow contract is paused before creating a user profile. If the platform is in an emergency "
"pause after a discovered exploit, new users should not be able to onboard and create additional "
"attack surface.",
[("Category","Security"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","1572-1778"),("Impact Level","Medium")],
["Add a pause-state check at the top of `onboard_user` by cross-calling the escrow contract's `get_platform_config().paused` flag when `escrow_contract` is set.",
 "Add a test that pauses the escrow contract and attempts onboarding, asserting the call reverts.",
 "Alternatively, add a local `is_paused` flag to `OnboardingConfig` to allow independent pausing."])),

dict(title="[SECURITY] has_active_contracts must enforce user authorization to prevent scraping (Issue #452)",
     labels=["security","onboarding"],
     body=make_body(
"`has_active_contracts` at `src/onboarding.rs` line 1787 returns whether a user has open "
"contracts. Issue #452 (line 2106 of onboarding_test.rs) requires user authorization to prevent "
"competitor scraping of trade activity. Without auth, a competitor can continuously poll this "
"endpoint to selectively undercut prices when sellers are between orders.",
[("Category","Security / Privacy"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","1787-1851"),("Impact Level","Medium")],
["Add `user.require_auth()` before reading `DataKey::ActiveContracts(user)`.",
 "Add `#[should_panic]` test for unauthorized access.",
 "Add positive test confirming the correct boolean for authorized caller.",
 "Extend TTL of the entry on read."])),

# ===== BUG / BUILD (21-30) =================================================

dict(title="[BUG] last_event tuple-field access fails after soroban-sdk API change - fix test.rs events indexing",
     labels=["bug","testing"],
     body=make_body(
"`cargo check --tests` reports 6 errors of type `E0609: no field '1'/'2' on type Option<(Address, "
"Vec<Val>, Val)>` in `src/test.rs` at lines 2559, 2567, 2584, 2592, 2601, and 2609. "
"`env.events().all().last()` now returns Option<...> instead of a raw tuple. All .1 and .2 "
"field accesses must be prefixed with `.unwrap()`.",
[("Category","Bug / Build blocker"),("Target File","`src/test.rs`"),
 ("Specific Lines","2559, 2567, 2584, 2592, 2601, 2609"),("Impact Level","Critical - prevents cargo test from running")],
["Apply `.unwrap()` before `.1` and `.2` at all 6 locations listed above.",
 "Run `cargo check --tests` and confirm zero E0609 errors remain.",
 "Run `cargo test` and verify all affected test functions pass."])),

dict(title="[BUG] Symbol::to_string() not in scope in onboarding.rs - missing alloc::string::ToString import",
     labels=["bug","build"],
     body=make_body(
"`cargo check --tests` reports `E0599: no method named 'to_string' found for struct "
"soroban_sdk::Symbol` at `src/onboarding.rs` lines 2149, 2255, and 3395. "
"`soroban_sdk::Symbol` implements `ToString` via `alloc::string::ToString` but the "
"trait is not in scope in this no_std crate.",
[("Category","Bug / Build blocker"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","2149, 2255, 3395"),("Impact Level","Critical")],
["Add `use crate::alloc::string::ToString;` immediately below the `use soroban_sdk::...` block at the top of `onboarding.rs`.",
 "Run `cargo check` and confirm zero E0599 errors for this file.",
 "Run affected tests (test_change_username_*, test_deactivate_*, test_reactivate_*) and confirm they pass."])),

dict(title="[BUG] Use of moved value `onboarding_contract` in expired_dispute_fee_test.rs:68",
     labels=["bug","testing"],
     body=make_body(
"`src/expired_dispute_fee_test.rs` line 56 moves `onboarding_contract` into "
"`Some(onboarding_contract)`, then tries to use it again at line 68, triggering "
"`E0382: use of moved value`. The fix is to clone the value before the first move.",
[("Category","Bug / Build blocker"),("Target File","`src/expired_dispute_fee_test.rs`"),
 ("Specific Lines","48-68"),("Impact Level","High - prevents this test module from compiling")],
["Add `.clone()` at line 56: `&Some(onboarding_contract.clone())`.",
 "Run `cargo check --tests` and confirm zero E0382 errors.",
 "Run `cargo test expired_dispute_fee_test` and confirm all tests pass."])),

dict(title="[BUG] Missing closing brace in test_process_verification_request_unauthorized causes entire module parse failure",
     labels=["bug","build"],
     body=make_body(
"The Rust parser reports `error: this file contains an unclosed delimiter` pointing to "
"`src/onboarding_test.rs:2157`. Root cause: `test_process_verification_request_unauthorized` "
"(line 764) is missing its closing `}` brace. Every subsequent function in the file is parsed "
"as nested inside the unclosed function, causing the entire module to fail compilation.",
[("Category","Bug / Build blocker"),("Target File","`src/onboarding_test.rs`"),
 ("Specific Lines","764-811"),("Impact Level","Critical - entire onboarding test module fails to compile")],
["Add `}` at the end of the `test_process_verification_request_unauthorized` function body (after line 810).",
 "Run `cargo check --tests` and confirm the parse error is gone.",
 "Run `cargo test onboarding_test` and confirm all tests pass."])),

dict(title="[BUG] Missing `use soroban_sdk::vec;` in min_release_window_test.rs causes macro resolution failure",
     labels=["bug","testing"],
     body=make_body(
"`cargo check --tests` reports `cannot find macro 'vec' in this scope` at "
"`src/min_release_window_test.rs` lines 339 and 437. The test file uses the `vec![...]` macro "
"but has not imported `soroban_sdk::vec`, which shadows the standard library's `vec!` macro in "
"no_std crates.",
[("Category","Bug / Build blocker"),("Target File","`src/min_release_window_test.rs`"),
 ("Specific Lines","339, 437"),("Impact Level","High")],
["Add `use soroban_sdk::vec;` at the top of `min_release_window_test.rs`.",
 "Run `cargo check --tests` and confirm the macro errors are resolved.",
 "Run `cargo test min_release_window_test` and confirm all tests pass."])),

dict(title="[BUG] Unused constant ONBOARD_CALL_FAILED inflates WASM binary and signals incomplete feature",
     labels=["bug","refactoring"],
     body=make_body(
"`src/lib.rs` line 168 defines `const ONBOARD_CALL_FAILED: Symbol = symbol_short!(\"OB_FAIL\");`. "
"The compiler warns `constant ONBOARD_CALL_FAILED is never used`. Unused constants inflate WASM "
"binary size and indicate a planned feature (emitting a failure event on cross-contract onboarding "
"calls) was never implemented.",
[("Category","Bug / Dead Code"),("Target File","`src/lib.rs`"),
 ("Specific Lines","168"),("Impact Level","Low - binary bloat, incomplete feature")],
["Either implement the intended feature by emitting an event with this symbol when the cross-contract onboarding call fails, or remove the constant.",
 "Run `cargo check` and confirm the `dead_code` warning is gone."])),

dict(title="[BUG] EscrowContract constant name violates Rust UPPER_SNAKE_CASE convention",
     labels=["bug","refactoring"],
     body=make_body(
"`src/lib.rs` line 796 defines `pub const EscrowContract: CraftNexusContract = CraftNexusContract;`. "
"The compiler warns `constant EscrowContract should have an upper case name`. In Rust, constants must "
"be UPPER_SNAKE_CASE. This naming violation triggers CI lint failures.",
[("Category","Bug / Style"),("Target File","`src/lib.rs`"),
 ("Specific Lines","796"),("Impact Level","Low")],
["Rename `EscrowContract` to `ESCROW_CONTRACT`.",
 "Update all references (grep for `EscrowContract` in the codebase).",
 "Run `cargo check` and confirm the naming warning is resolved."])),

dict(title="[BUG] get_onboarding_client helper is defined but never called - remove or complete integration",
     labels=["bug","dead-code"],
     body=make_body(
"The compiler warns `associated function 'get_onboarding_client' is never used --> src/lib.rs:1237`. "
"This helper was scaffolded to enable cross-contract calls from the escrow contract to the onboarding "
"contract, but the integration was never completed. Dead associated functions increase code review burden.",
[("Category","Bug / Dead Code"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1237-1250"),("Impact Level","Low")],
["Audit whether cross-contract onboarding calls are intended in the final architecture.",
 "If yes, implement the full integration and add tests.",
 "If no, remove `get_onboarding_client` and related scaffolding.",
 "Run `cargo check` and confirm the dead-code warning is resolved."])),

dict(title="[BUG] previous_admin variable assigned but never read in update_admin - missing audit trail event",
     labels=["bug","dead-code"],
     body=make_body(
"`src/lib.rs` line 1650 declares `let previous_admin = config.admin.clone();`. The compiler warns "
"`unused variable: previous_admin`. The variable was likely introduced to emit an `AdminChanged` "
"event with both old and new admin addresses, but the event emission was never implemented. This "
"creates a missing audit trail for admin changes.",
[("Category","Bug / Incomplete Feature"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1650"),("Impact Level","Low - signals missing audit trail event")],
["Emit an `AdminChangedEvent { previous_admin, new_admin }` at the end of `update_admin` to create an auditable trail.",
 "Alternatively, rename to `_previous_admin` if the event is explicitly out of scope.",
 "Add a test that listens for the admin-change event and verifies the payload."])),

dict(title="[BUG] mutable queue binding in prune_matured_stake_deposits declared mut but never mutated - potential silent no-op",
     labels=["bug","refactoring"],
     body=make_body(
"`src/lib.rs` approximately line 4516 declares `let mut queue: soroban_sdk::Vec<StakeDeposit> = env...`. "
"The compiler warns `variable does not need to be mutable`. If the queue is never mutated through this "
"binding, the pruning logic may not be correctly modifying the stake queue in persistent storage, "
"resulting in a silent no-op prune that blocks new stake deposits when the queue fills.",
[("Category","Bug / Correctness"),("Target File","`src/lib.rs`"),
 ("Specific Lines","~4516"),("Impact Level","Medium - potential silent no-op pruning")],
["Audit whether `queue` mutations are written back to storage via `env.storage().persistent().set(...)`.",
 "If the storage write is missing, add it.",
 "Remove the `mut` keyword once confirmed the design is intentional.",
 "Add a test that prunes the queue and verifies the storage entry is updated."])),

# ===== PERFORMANCE / STORAGE (31-45) =======================================

dict(title="[PERFORMANCE] Extend TTL after every persistent write to prevent storage archival (Issue #533)",
     labels=["performance","storage"],
     body=make_body(
"On Stellar Soroban, persistent storage entries have a Time-To-Live (TTL). Entries not refreshed "
"via `extend_ttl()` are archived and become inaccessible until explicitly restored. Issue #533 "
"tracks comprehensive TTL coverage. Several storage write paths in `src/lib.rs` and "
"`src/onboarding.rs` are missing `Self::extend_persistent(&env, &key)` calls after "
"`env.storage().persistent().set(...)`.",
[("Category","Performance / Reliability"),("Target File","`src/lib.rs`, `src/onboarding.rs`"),
 ("Specific Lines","Multiple"),("Impact Level","High - silent data loss on low-activity deployments")],
["Audit every `env.storage().persistent().set(...)` call and confirm `Self::extend_persistent(...)` follows immediately.",
 "Create a checklist of all DataKey variants and verify TTL coverage.",
 "Add test assertions that read entries after simulated ledger advancement to confirm they are not archived."])),

dict(title="[PERFORMANCE] Replace monolithic AllEscrowIds Vec with O(1) indexed append pattern (Issue #515 / #226)",
     labels=["performance","storage"],
     body=make_body(
"Issue #515 (line 1436 of `lib.rs`) documents the migration from a monolithic `AllEscrowIds Vec<u32>` "
"to the indexed append pattern (`DataKey::EscrowIndex(count)` + `DataKey::EscrowCount`). This O(1) "
"pattern avoids loading and rewriting the entire Vec on each escrow creation. The migration helper "
"`migrate_user_escrows` (line 2382) must be verified for correctness.",
[("Category","Performance / Storage"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1434-1450, 2382-2443"),("Impact Level","High - O(n) write on each escrow creation blocks scalability")],
["Run the migration helper against a testnet deployment with >1000 escrows.",
 "Add a test that creates 100 escrows and verifies `EscrowCount` equals 100.",
 "After verifying correctness, plan removal of the legacy `AllEscrowIds` key in the next contract version."])),

dict(title="[PERFORMANCE] WhitelistedTokens monolithic map migration to indexed storage needs audit (scalability)",
     labels=["performance","storage"],
     body=make_body(
"`SCALABILITY_IMPROVEMENTS.md` documents that the legacy `WhitelistedTokens Map<Address, bool>` was "
"replaced with individual `WhitelistedTokenIndexed(Address)` keys. Each individual entry is ~36 bytes "
"vs. the 64KB monolithic map limit (~1800 tokens). The migration helper `migrate_whitelist_storage` "
"must be audited and tested with a large token list.",
[("Category","Performance / Storage"),("Target File","`src/lib.rs`"),
 ("Specific Lines","2094-2145"),("Impact Level","High")],
["Add a test that populates 50+ whitelisted tokens via the legacy map, runs migration, then verifies all tokens are accessible.",
 "Confirm `WhitelistedTokenCount` is accurate after migration.",
 "Add a scalability_test that verifies the individual storage pattern beyond 1800 tokens without hitting limits."])),

dict(title="[PERFORMANCE] ArtisanStakeQueue pruning correctness verification (MAX_STAKE_QUEUE_SIZE=50)",
     labels=["performance","storage"],
     body=make_body(
"`SCALABILITY_IMPROVEMENTS.md` documents `ArtisanStakeQueue` bounded at `MAX_STAKE_QUEUE_SIZE = 50` "
"deposits per artisan with `STAKE_QUEUE_PRUNE_THRESHOLD = 40`. The `prune_matured_stake_deposits` "
"function must be verified to correctly compact the indexed queue and update counts. See also the "
"dead `mut` variable bug issue.",
[("Category","Performance / Storage"),("Target File","`src/lib.rs`"),
 ("Specific Lines","prune_matured_stake_deposits function"),("Impact Level","High - queue exhaustion blocks new stake deposits")],
["Add a test that fills the queue to 49 entries and confirms no pruning occurs.",
 "Add a test that fills to 41 entries and confirms pruning removes all matured deposits.",
 "After pruning, verify `ArtisanStakeQueueCount` is correctly decremented.",
 "Test the edge case where all deposits are matured and the queue empties completely."])),

dict(title="[PERFORMANCE] Replace Symbol::new() with symbol_short! for event topic symbols under 9 characters",
     labels=["performance","storage"],
     body=make_body(
"Soroban documentation recommends `symbol_short!(\"...\")` for symbols <= 9 characters (encoded in "
"the Val type header, zero storage cost) over `Symbol::new(&env, \"...\")` which allocates a heap "
"string on the host. Several event topic symbols in `src/lib.rs` and `src/onboarding.rs` use "
"`Symbol::new(...)` for short strings that qualify for `symbol_short!`.",
[("Category","Performance"),("Target File","`src/lib.rs`, `src/onboarding.rs`"),
 ("Specific Lines","Multiple event emission sites"),("Impact Level","Medium - unnecessary CPU instructions per event")],
["Audit all `Symbol::new(&env, \"...\")` calls in event topic positions.",
 "Replace any strings <= 9 ASCII characters with `symbol_short!(\"...\")`.",
 "Run `cargo check` and `cargo test` to confirm behavior is unchanged."])),

dict(title="[PERFORMANCE] Verification history may use O(n) linear scan - migrate to indexed circular-buffer (Issue #82)",
     labels=["performance","storage"],
     body=make_body(
"`src/onboarding.rs` (Feature #83 comment at line 1121) notes verification history uses a "
"circular-buffer rotation for active contracts. However, `get_verification_history` at line 3091 "
"may still perform an O(n) linear scan. With `MAX_VERIFICATION_HISTORY_PER_USER` entries (Issue "
"#519), the O(n) scan wastes CPU on every read.",
[("Category","Performance"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","3091-3136"),("Impact Level","Medium")],
["Confirm the verification history uses `DataKey::VerificationHistoryEntry(user, index)` indexed storage rather than a monolithic Vec.",
 "If it still uses a Vec, migrate to the indexed pattern.",
 "Add a performance test that reads a full history (max entries) and verifies the read budget is within Soroban limits."])),

dict(title="[PERFORMANCE] Extend TTL on config read to prevent storage expiry on quiescent deployments (Issue #423)",
     labels=["performance","storage"],
     body=make_body(
"`src/lib.rs` line 1716 comments `// Issue #423: extend TTL on read to prevent storage expiry`. "
"`PlatformConfig` is read on almost every function call but not always written. On low-activity "
"testnets or after launch delays, the config entry could expire and archive, bricking the contract.",
[("Category","Performance / Reliability"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1716, get_platform_config function"),("Impact Level","High")],
["Confirm `Self::extend_persistent_read(&env, &DataKey::PlatformConfig)` is called inside `get_platform_config`.",
 "Add the same TTL-on-read pattern to `OnboardingConfig` reads in `src/onboarding.rs`.",
 "Add a test that simulates a long ledger gap (advance ledger timestamp) and confirms the config is still readable."])),

dict(title="[PERFORMANCE] get_escrows_by_buyer and get_escrows_by_seller must paginate results to avoid memory exhaustion",
     labels=["performance","storage"],
     body=make_body(
"`get_escrows_by_buyer` (line 2880) and `get_escrows_by_seller` (line 2953) return all escrow IDs "
"for a user. For high-volume artisans with thousands of trades, returning the entire list in a single "
"call would exhaust the Soroban host's memory budget and fail. Both functions use the indexed storage "
"pattern but may not enforce a page-size limit.",
[("Category","Performance"),("Target File","`src/lib.rs`"),
 ("Specific Lines","2880-3025"),("Impact Level","High - DoS for high-volume users")],
["Add `page_size: u32` and `page: u32` parameters to both functions.",
 "Return at most `page_size` entries starting from `page * page_size`.",
 "Add a test with 200 escrows and verify pagination returns correct subsets.",
 "Update README with the new pagination parameters."])),

dict(title="[PERFORMANCE] UserProfile struct carries optional string fields - flatten to reduce persistent storage rent",
     labels=["performance","storage"],
     body=make_body(
"On Soroban, persistent rent is proportional to entry size. `UserProfile` carries "
"`portfolio_cid: Option<String>` and may expand in the future. Integration notes for component "
"#26 (UserMetrics) warn: 'Avoid adding Vec or Map fields here; derived counters belong in "
"separate indexed keys.'",
[("Category","Performance / Storage"),("Target File","`src/onboarding.rs`"),
 ("Specific Lines","UserProfile struct definition"),("Impact Level","Medium")],
["Audit all `contracttype` structs for Vec or Map fields.",
 "Move any Vec/Map fields into separate indexed storage keys.",
 "Update `versioned-state-migration.md` to document the schema change.",
 "Add a migration helper for any struct shape changes."])),

dict(title="[PERFORMANCE] Short-circuit no-op calls in set_onboarding_contract to avoid unnecessary writes (Issue #527)",
     labels=["performance","storage"],
     body=make_body(
"`src/lib.rs` line 1787 comments: `// Issue #527 - short-circuit on the no-op call before paying`. "
"If the onboarding contract address being set is identical to the currently stored value, the function "
"should return early without writing to storage, avoiding an unnecessary persistent write and TTL cost.",
[("Category","Performance"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1787-1800"),("Impact Level","Low")],
["Read the current onboarding contract address.",
 "If it equals the new address, return immediately.",
 "Add a test that calls `set_onboarding_contract` twice with the same value and asserts only one storage write occurs."])),

dict(title="[PERFORMANCE] Audit fee_token_configs migration to indexed storage for production correctness",
     labels=["performance","storage"],
     body=make_body(
"`migrate_fee_token_configs` at `src/lib.rs` line 3349 migrates legacy fee token configuration to "
"indexed storage. The `FeeTokenIndex` + `FeeTokenConfig(Address)` indexed keys replace the legacy "
"monolithic `Map<Address, FeeTokenInfo>`. This migration must be audited and tested with a "
"production-sized dataset to confirm no fees are lost.",
[("Category","Performance / Migration"),("Target File","`src/lib.rs`"),
 ("Specific Lines","3349-3450"),("Impact Level","High - incorrect migration causes fee configuration loss")],
["Add a test with 20 fee token configs that runs migration and verifies all configs are accessible via `get_fee_token_config`.",
 "Verify `migrate_fee_token_configs` is idempotent (safe to run twice).",
 "Add a dry-run mode or event emission so operators can verify migration success before committing."])),

dict(title="[PERFORMANCE] Batch escrow buyer/seller count accumulation has O(n^2) Map lookups in inner loop",
     labels=["performance","storage"],
     body=make_body(
"`create_batch_escrow` at `src/lib.rs` line 4867 collects buyer/seller counts in a Map<Address, u32> "
"and writes them at the end (line 4941). However, the in-memory Map is re-read at every inner loop "
"iteration when calculating existing counts, causing O(n^2) lookups in the worst case for a large batch.",
[("Category","Performance"),("Target File","`src/lib.rs`"),
 ("Specific Lines","4867-4975"),("Impact Level","Medium")],
["Restructure the accumulation loop so buyer/seller counts are computed in a single pass without repeated reads.",
 "Add a benchmark test (batch of 20 escrows) that measures ledger entry write count and confirms it scales linearly."])),

dict(title="[PERFORMANCE] IPFS CID validation allocates soroban_sdk::Bytes per call - inline the check",
     labels=["performance","storage"],
     body=make_body(
"The IPFS CID validation helper in `src/lib.rs` line 1121 (Issue #521) allocates a `soroban_sdk::Bytes` "
"object to verify Base58btc encoding. On `create_escrow_with_metadata`, this check is performed twice "
"(for `ipfs_hash` and `metadata_hash`), doubling the allocation cost.",
[("Category","Performance"),("Target File","`src/lib.rs`"),
 ("Specific Lines","1121-1200"),("Impact Level","Low-Medium")],
["Refactor the validation to avoid allocating a `soroban_sdk::Bytes` object.",
 "Validate directly against the byte slice using a const lookup table.",
 "Add a test with a 46-character CIDv0 and a 59-character CIDv1 and confirm validation passes in both cases."])),

dict(title="[PERFORMANCE] Recurring escrow ID allocation must use checked_add to prevent silent ID collision (Issue #233)",
     labels=["performance","storage"],
     body=make_body(
"`docs/deprecated-storage.md` documents `DataKey::NextRecurringEscrowId` (Issue #233) noting that "
"allocation past `MAX_RECURRING_ESCROW_ID` must use `checked_add` to avoid silent wrapping into an "
"existing ID. `src/lib.rs` line 6013 comments the bounded allocation. Verify the implementation "
"uses `checked_add(1)` and returns an error (not panic) at the ceiling.",
[("Category","Performance / Correctness"),("Target File","`src/lib.rs`"),
 ("Specific Lines","6013-6050"),("Impact Level","High - silent ID collision if overflow unchecked")],
["Confirm `checked_add(1)` is used and `Error::RecurringEscrowIdExhausted` is returned (not a panic) when the ceiling is hit.",
 "Add a test that fills IDs to `MAX_RECURRING_ESCROW_ID - 1` and asserts the next call returns the error.",
 "Document the ceiling value in README."])),

dict(title="[PERFORMANCE] Remove legacy StakeCooldownEnd mirror writes to eliminate redundant storage costs (Issue #235)",
     labels=["performance","storage"],
     body=make_body(
"`docs/deprecated-storage.md` documents `DataKey::StakeCooldownEnd(Address)` (Issue #235) as "
"deprecated but still mirrored on every `stake_tokens` and `unstake_tokens` call. Each mirror write "
"costs extra ledger-entry storage and TTL fees. Once off-chain readers are updated, this write should "
"be removed.",
[("Category","Performance / Storage"),("Target File","`src/lib.rs`"),
 ("Specific Lines","stake_tokens, unstake_tokens functions"),("Impact Level","Low-Medium")],
["Confirm off-chain indexers no longer read `DataKey::StakeCooldownEnd`.",
 "Remove the mirror writes from `stake_tokens` and `unstake_tokens`.",
 "Remove or archive the `purge_stake_cooldown_end` admin helper.",
 "Remove `DataKey::StakeCooldownEnd` from the enum.",
 "Update `deprecated-storage.md` to mark this track as complete."])),

# ===== ARCHITECTURE (46-55) ================================================

dict(title="[ARCHITECTURE] Decouple Onboarding and Escrow contracts to reduce cross-contract coupling risk",
     labels=["architecture","enhancement"],
     body=make_body(
"The Onboarding and Escrow contracts are strongly coupled: the escrow contract calls "
"`update_user_metrics`, `update_active_contracts`, and `update_reputation` on the onboarding "
"contract, and the onboarding contract reads `has_active_escrows` from the escrow contract. "
"This tight coupling means both contracts must be upgraded together, increasing governance risk.",
[("Category","Architecture"),("Impact Level","Medium - long-term maintainability risk")],
["Document the full cross-contract call graph.",
 "Identify which calls can be replaced by event subscriptions.",
 "Propose a MetricsAggregator contract or event-driven metrics update model.",
 "Add an Architecture Decision Record (ADR) in `docs/` describing the chosen approach."])),

dict(title="[ARCHITECTURE] Versioned state migration missing for Escrow struct schema changes post-deployment",
     labels=["architecture","migration"],
     body=make_body(
"`docs/versioned-state-migration.md` documents versioning for `UserProfile` but the `Escrow` struct "
"contains fields like `batch_id: Option<u64>` and `metadata_hash: Option<BytesN<32>>` added "
"post-deployment without a version bump or migration script. Legacy escrows will deserialize with "
"default values, causing silent behavioral differences.",
[("Category","Architecture / Migration"),("Target File","`src/lib.rs`, docs/versioned-state-migration.md"),
 ("Impact Level","High - silent deserialization inconsistencies for legacy escrows")],
["Add a `version: u32` field to the `Escrow` struct.",
 "Define `CURRENT_ESCROW_VERSION` and implement a `migrate_escrow` helper.",
 "Update `docs/versioned-state-migration.md` with the migration plan.",
 "Add a test that deserializes a legacy `Escrow` (without new fields) and confirms it migrates correctly."])),

dict(title="[ARCHITECTURE] Error code enum lacks structured categories - add error taxonomy for better off-chain handling",
     labels=["architecture","documentation"],
     body=make_body(
"The `Error` enum in `src/lib.rs` lines 27-110 defines 34+ error codes as a flat list. Without "
"taxonomy, callers cannot distinguish: Authorization failures (rollback immediately), State transition "
"errors (retry after state change), Configuration errors (operator must act), and Transient errors "
"(retry later). This makes off-chain error handling and indexer triage difficult.",
[("Category","Architecture / Developer Experience"),("Target File","`src/lib.rs`"),
 ("Impact Level","Medium")],
["Group error codes into sub-ranges (e.g., 1-9 = Auth, 10-19 = State, 20-29 = Config, 30-39 = Limits).",
 "Document each range in the error enum's module-level doc comment.",
 "Add an `is_retryable(error: Error) -> bool` helper.",
 "Update README Error Codes section."])),

dict(title="[ARCHITECTURE] Event schema not validated against snapshot files on every test run - add regression guards",
     labels=["architecture","testing"],
     body=make_body(
"`test_snapshots/` contains JSON snapshots of emitted events as regression guards. However, there "
"is no automated check that forces snapshot updates when event structs change. If a developer "
"modifies `EscrowEvent` or `UserOnboardedEvent`, the snapshots may silently become stale.",
[("Category","Architecture / Testing"),("Target File","test_snapshots/ directory"),
 ("Impact Level","Medium")],
["Add a CI step that runs `cargo test --update-snapshots` and fails if any snapshot changes without explicit approval.",
 "Document the snapshot update workflow in README.",
 "Add a test that verifies each event struct matches its JSON schema exactly."])),

dict(title="[ARCHITECTURE] Referral rewards system deprecated without cleanup - resolve or archive Issue #234",
     labels=["architecture","technical-debt"],
     body=make_body(
"`src/lib.rs` line 5173 comments `// Referral Rewards (#105, DEPRECATED - see Issue #234)`. "
"The referral reward system was scoped but never shipped. The deprecated `DataKey::ReferralRewardBps` "
"key remains in the enum to preserve ABI compatibility but wastes space in the type system and "
"increases cognitive overhead for contributors.",
[("Category","Architecture / Technical Debt"),("Target File","`src/lib.rs`, docs/deprecated-storage.md"),
 ("Impact Level","Low - technical debt accumulation")],
["Decide: ship a minimal referral system or permanently remove it.",
 "If removing: bump the contract version, remove `DataKey::ReferralRewardBps`, and update `deprecated-storage.md`.",
 "If implementing: create a new issue with the referral feature specification."])),

dict(title="[ARCHITECTURE] onboard_user should emit error events instead of panicking to improve indexer observability",
     labels=["architecture","enhancement"],
     body=make_body(
"`onboard_user` panics on validation failures (duplicate username, invalid role, etc.). Soroban panics "
"roll back the transaction and emit no events. Off-chain indexers cannot distinguish between 'user "
"tried to register with an existing username' and 'network error' without parsing host error codes. "
"The constant `ONBOARD_CALL_FAILED` (currently dead code) was apparently intended for this purpose.",
[("Category","Architecture / Developer Experience"),("Target File","`src/onboarding.rs`"),
 ("Impact Level","Medium")],
["Return `Result<UserProfile, Error>` from `onboard_user` instead of panicking on validation failures.",
 "Emit a failure-reason event (using `ONBOARD_CALL_FAILED`) before returning Err.",
 "Update all tests to use `.try_onboard_user(...)` and assert the specific error code.",
 "Document the new return-type contract in README."])),

dict(title="[ARCHITECTURE] auto_verify_user should emit a dedicated AutoVerifiedEvent distinct from manual verification",
     labels=["architecture","enhancement"],
     body=make_body(
"`auto_verify_user` at `src/onboarding.rs` line 2843 automatically verifies an artisan when they "
"cross the escrow count and volume thresholds. The function calls `verify_user` which emits a "
"`UserVerified` event, but the event does not distinguish between manual admin verification and "
"automatic threshold-based verification.",
[("Category","Architecture"),("Target File","`src/onboarding.rs`"),
 ("Impact Level","Low")],
["Create a new `AutoVerifiedEvent { user, escrow_count, volume }` struct.",
 "Emit this event instead of (or in addition to) `UserVerified` when auto-verification triggers.",
 "Add a test that asserts the auto-verified event is emitted with correct payload values."])),

dict(title="[ARCHITECTURE] Separate Escrow lifecycle events from Config-change events using consistent topic namespacing",
     labels=["architecture","enhancement"],
     body=make_body(
"The event stream in the escrow contract mixes lifecycle events (EscrowCreated, FundsReleased, "
"DisputeOpened) with administrative events (ConfigUpdated, TokenWhitelisted). Indexers that only "
"care about financial flows must filter the entire event stream, increasing processing costs.",
[("Category","Architecture"),("Target File","`src/lib.rs`"),
 ("Impact Level","Low")],
["Add a consistent event-class prefix to all event topics: `escrow.*`, `admin.*`, `stake.*`.",
 "Update README Event Reference section with the new taxonomy.",
 "Update existing event snapshot tests to reflect the new topic format."])),

dict(title="[ARCHITECTURE] create_unfunded_escrow has no funding timeout - unfunded stubs accrue rent indefinitely",
     labels=["architecture","escrow"],
     body=make_body(
"`create_unfunded_escrow` (line 2699) creates an escrow stub that must be funded via `fund_escrow` "
"(line 2811). If the buyer never calls `fund_escrow`, the stub occupies persistent storage "
"indefinitely, accruing rent costs for the seller and the platform. `cancel_unfunded_escrow` "
"(line 2852) only allows voluntary cancellation by the buyer.",
[("Category","Architecture"),("Target File","`src/lib.rs`"),
 ("Impact Level","Medium")],
["Add a `funding_deadline: u64` ledger timestamp to unfunded escrows.",
 "Allow any party to call `cancel_unfunded_escrow` after the deadline.",
 "Add an `auto_cancel_unfunded` function callable by the platform admin.",
 "Add tests for all deadline scenarios."])),

dict(title="[ARCHITECTURE] Dispute resolution lacks an arbitrator time-lock - arbitrators can delay indefinitely",
     labels=["architecture","escrow"],
     body=make_body(
"`docs/ArbitratorTechnicalGuide.md` describes the arbitrator role but once a dispute is opened, "
"the arbitrator has no deadline to resolve it. A compromised or negligent arbitrator can block a "
"dispute indefinitely, leaving funds locked. The `DisputeExpired` error (Error #16) suggests a "
"deadline system is planned but not yet implemented.",
[("Category","Architecture"),("Target File","`src/lib.rs`, docs/ArbitratorTechnicalGuide.md"),
 ("Impact Level","High - fund lockup due to arbitrator inaction")],
["Add `dispute_deadline: u64` (dispute_opened_at + DISPUTE_RESOLUTION_WINDOW) to the `Escrow` struct.",
 "Implement `resolve_expired_dispute` that refunds or releases based on a configurable policy after the deadline.",
 "Update `ArbitratorTechnicalGuide.md` with the deadline policy.",
 "Add tests for all deadline scenarios."])),

# ===== TESTING (56-65) =====================================================

dict(title="[TESTING] Add comprehensive fuzz tests for IPFS CID validation - property-based approach",
     labels=["testing","enhancement"],
     body=make_body(
"The IPFS CID validation helper is a critical input-validation gate accepting CIDv0 (Base58btc) "
"and CIDv1 (Base32) strings. Hand-crafted tests cover happy paths and a few edge cases, but "
"property-based fuzz testing would surface unexpected panics or incorrect acceptance of malformed "
"CIDs that hand-crafted tests cannot enumerate.",
[("Category","Testing"),("Target File","`src/lib.rs`"),
 ("Impact Level","Medium")],
["Add a property-based test using `arbitrary::Arbitrary` that generates random byte strings and asserts the CID validator never panics.",
 "Add specific boundary tests: 45-char CIDv0, 46-char CIDv0, 58-char CIDv1, 59-char CIDv1.",
 "Confirm the validator rejects CIDs with invalid Base58btc characters (0, O, I, l)."])),

dict(title="[TESTING] reentrancy_test.rs missing test for fund_escrow CEI pattern - add coverage",
     labels=["testing","security"],
     body=make_body(
"`test_snapshots/reentrancy_test/` contains snapshots for `release_funds`, `refund`, "
"`resolve_dispute`, `auto_release`, and `cancel_recurring_escrow` CEI patterns, but **not** for "
"`fund_escrow`. A reentrancy during the `fund_escrow` token transfer could allow a malicious buyer "
"to create a funded escrow without actually transferring tokens.",
[("Category","Testing / Security"),("Target File","`src/reentrancy_test.rs`"),
 ("Impact Level","High")],
["Add `test_fund_escrow_cei_pattern` to `src/reentrancy_test.rs`.",
 "Verify that the escrow status is set to `Active` **before** the token transfer in `fund_escrow`.",
 "Add the corresponding snapshot file."])),

dict(title="[TESTING] Add snapshot tests for all batch escrow boundary scenarios (Issue #111)",
     labels=["testing","escrow"],
     body=make_body(
"`test_snapshots/test/test_create_batch_escrow_*.json` covers success, invalid amount, and "
"same-buyer-seller failures, but is missing scenarios for: batch at maximum size limit (20 "
"escrows), batch exceeding maximum size (21 escrows, should all fail), and batch with distinct "
"buyers requiring multi-party auth.",
[("Category","Testing"),("Target File","`src/test.rs`"),
 ("Impact Level","Medium")],
["Add `test_create_batch_escrow_at_max_size` (20 escrows, all succeed).",
 "Add `test_create_batch_escrow_exceeds_max_size` (21 escrows, all fail).",
 "Add `test_create_batch_escrow_multi_buyer_unauthorized` (two buyers, second without auth, assert panic)."])),

dict(title="[TESTING] Add snapshot tests for admin recovery edge cases",
     labels=["testing","escrow"],
     body=make_body(
"`recover_admin_access` (line 2444) handles admin recovery but has no dedicated snapshot tests "
"in `test_snapshots/test/`. Edge cases not covered: recovery with zero cooldown (should fail), "
"recovery where recovery address is same as current admin (should fail), and successful recovery "
"with valid cooldown.",
[("Category","Testing"),("Target File","`src/lib.rs`, `src/test.rs`"),
 ("Impact Level","High")],
["Add `test_recover_admin_access_zero_cooldown_fails`.",
 "Add `test_recover_admin_access_same_address_fails`.",
 "Add `test_recover_admin_access_success`.",
 "Generate snapshot files for all three tests."])),

dict(title="[TESTING] Add governance test coverage for multi-sig upgrade threshold boundary scenarios (Issue #95)",
     labels=["testing","escrow"],
     body=make_body(
"`test.rs` line 855 opens a governance (#95) test section but coverage for multi-signature WASM "
"upgrade scenarios is incomplete. Missing scenarios: threshold of 1 (single-sig), threshold equals "
"number of signers exactly, signers list changed after a proposal is active, and proposal expires "
"and is re-proposed.",
[("Category","Testing"),("Target File","`src/test.rs`"),
 ("Impact Level","High")],
["Add tests for each missing scenario listed above.",
 "Confirm `get_upgrade_history` records each successful upgrade.",
 "Add snapshot files for all new test cases."])),

dict(title="[TESTING] scalability_test.rs missing test for EscrowCount/BuyerEscrowCount/SellerEscrowCount sync at scale",
     labels=["testing","storage"],
     body=make_body(
"`create_single_escrow` maintains `AllEscrowIds`, `BuyerEscrowCount`, `SellerEscrowCount`, and "
"the global `EscrowCount` in sync. If any write fails or is out of order, counts diverge and "
"pagination breaks. `test_snapshots/scalability_test/` does not have a test explicitly verifying "
"all three counters after 100+ escrows.",
[("Category","Testing"),("Target File","`src/scalability_test.rs`"),
 ("Impact Level","High")],
["Add a test that creates 100 escrows for the same buyer/seller pair.",
 "Assert `get_escrows_by_buyer().len() == 100`.",
 "Assert `EscrowCount == 100` via `get_platform_config().total_escrows`.",
 "Assert buyer and seller counts equal 100 each."])),

dict(title="[TESTING] enhanced_features_test.rs missing test for reactivate_profile after username reclaimed by another user",
     labels=["testing","onboarding"],
     body=make_body(
"`enhanced_features_test.rs` line 188 references Issue #115 (reactivate_profile). The snapshot "
"`test_reactivate_profile_username_taken_fails.1.json` covers the taken-username case, but there "
"is no test for: deactivated user A's username is released -> user B claims A's old username -> "
"A attempts reactivation -> asserts the call panics.",
[("Category","Testing"),("Target File","`src/enhanced_features_test.rs`"),
 ("Impact Level","Medium")],
["Add `test_reactivate_profile_after_username_claimed_by_another`.",
 "Sequence: deactivate user A -> user B claims A's old username -> A attempts reactivation -> assert panic.",
 "Add the corresponding snapshot file."])),

dict(title="[TESTING] Add dry-run batch validation tests for all invalid metadata combinations (DevEx #119)",
     labels=["testing","escrow"],
     body=make_body(
"`test.rs` line 2797 opens the DevEx #119 dry-run batch validation section. Snapshot files exist "
"for basic validation failures, but missing: CIDv0 with invalid length, CIDv1 with wrong version "
"prefix, metadata_hash with wrong byte length (not 32 bytes), and batch with a mix of valid and "
"invalid metadata hashes.",
[("Category","Testing"),("Target File","`src/test.rs`"),
 ("Impact Level","Medium")],
["Add `test_validate_batch_creation_invalid_cidv0_length`.",
 "Add `test_validate_batch_creation_cidv1_wrong_prefix`.",
 "Add `test_validate_batch_creation_mixed_valid_invalid_metadata`.",
 "Confirm the error in each case is `Error::InvalidMetadataHash` or the appropriate CID error."])),

dict(title="[TESTING] Reputation system tests missing zero-trade edge case and overflow guard (Issue #100)",
     labels=["testing","onboarding"],
     body=make_body(
"`onboarding_test.rs` line 924 opens the Issue #100 (Reputation System / Trust Score) test section. "
"Tests cover incrementing counters, but missing: `update_reputation` with zero successful and zero "
"disputed trades (should be a no-op or reset), and extremely high trade counts to verify the "
"overflow guard.",
[("Category","Testing"),("Target File","`src/onboarding_test.rs`"),
 ("Impact Level","Low")],
["Add `test_reputation_zero_trades_no_op`.",
 "Add `test_reputation_max_trades_no_overflow` (verify u32::MAX is handled without panic).",
 "Add snapshot files for both new tests."])),

dict(title="[TESTING] Volume normalization tests missing for tokens with 7, 8, and 18 decimal places (Issue #427)",
     labels=["testing","onboarding"],
     body=make_body(
"`update_user_metrics` normalizes volume to 7 decimal places before accumulation (Issue #427 / "
"component #26). The existing test may not cover tokens with exactly 7, 8, and 18 decimal places. "
"A normalization bug would silently cause auto-verification thresholds to be compared against "
"incorrectly scaled values, enabling fraudulent verification.",
[("Category","Testing"),("Target File","`src/onboarding_test.rs`"),
 ("Impact Level","High")],
["Add `test_volume_normalization_7_decimal_token` (no normalization needed).",
 "Add `test_volume_normalization_8_decimal_token` (divide by 10).",
 "Add `test_volume_normalization_18_decimal_token` (divide by 10^11).",
 "Confirm auto-verification triggers at the correct raw threshold in each case."])),

# ===== DOCUMENTATION (66-72) ===============================================

dict(title="[DOCS] Document all DataKey variants with TTL management strategy in a central storage reference",
     labels=["documentation"],
     body=make_body(
"`src/lib.rs` defines 40+ `DataKey` variants. Developers and auditors need a reference mapping each "
"key to: its storage type (Persistent/Temporary/Instance), TTL management strategy (extend on read, "
"extend on write, both, or never), and maximum size estimate. This information is scattered across "
"code comments but has no central reference.",
[("Category","Documentation"),("Impact Level","Medium")],
["Create `docs/storage-reference.md` with a table of all `DataKey` variants.",
 "Add columns: Key Variant | Storage Type | TTL Strategy | Max Entry Size.",
 "Link to `deprecated-storage.md` for deprecated keys."])),

dict(title="[DOCS] ArbitratorTechnicalGuide.md does not document the dispute deadline policy",
     labels=["documentation"],
     body=make_body(
"`docs/ArbitratorTechnicalGuide.md` describes the arbitrator role but does not mention any deadline "
"for dispute resolution. The guide should document: how long an arbitrator has to resolve a dispute, "
"what happens if the deadline passes (DisputeExpired error), and how the admin can override a stalled "
"arbitrator.",
[("Category","Documentation"),("Impact Level","Medium")],
["Add a 'Dispute Resolution Deadline' section to `ArbitratorTechnicalGuide.md`.",
 "Document the `resolve_expired_dispute` function once implemented.",
 "Add an FAQ entry: 'What if my arbitrator does not respond?'"])),

dict(title="[DOCS] README.md event reference section is incomplete - document all events from both contracts",
     labels=["documentation"],
     body=make_body(
"README.md has an Event Reference section but may not list all events emitted by both contracts. "
"Missing events likely include: ArtisanFeeTierUpdatedEvent, BatchEscrowCreatedEvent, "
"AutoVerifiedEvent, StakeDepositedEvent, StakeWithdrawnEvent, etc. Off-chain indexers that are "
"unaware of events will miss critical data.",
[("Category","Documentation"),("Impact Level","Medium")],
["Audit all `env.events().publish(...)` calls in `src/lib.rs` and `src/onboarding.rs`.",
 "Create a table in README Event Reference: Event Name | Topics | Data Fields.",
 "Ensure each event struct has a `///` doc-comment documenting the fields."])),

dict(title="[DOCS] versioned-state-migration.md needs a step-by-step migration runbook for each schema version",
     labels=["documentation"],
     body=make_body(
"`docs/versioned-state-migration.md` exists but its content is brief. It should include a step-by-step "
"runbook for each migration version: Pre-migration checks (verify current version), Migration "
"invocation command (`stellar contract invoke -- migrate_...`), and Post-migration verification.",
[("Category","Documentation"),("Impact Level","Medium")],
["Add a runbook section for the `UserProfile` v1 -> v2 migration.",
 "Add runbook for the `WhitelistedTokens` map -> individual key migration.",
 "Add runbook for the `ArtisanStakeQueue` Vec -> indexed queue migration."])),

dict(title="[DOCS] Contract addresses in README.md and stellar.toml should be kept in sync - add automated check",
     labels=["documentation"],
     body=make_body(
"README.md has a Contract Addresses section and `stellar.toml` has contract references. These two "
"sources can drift out of sync after re-deployments. There is no automated check to ensure they match.",
[("Category","Documentation"),("Impact Level","Low")],
["Add a CI step that reads contract addresses from `stellar.toml` and verifies they match the README.",
 "Alternatively, source contract addresses from a single `addresses.json` file that both `stellar.toml` and README are generated from."])),

dict(title="[DOCS] Add CONTRIBUTING.md with build, test, and PR workflow for new contributors",
     labels=["documentation"],
     body=make_body(
"The repository lacks a `CONTRIBUTING.md`. New contributors must discover the build process, test "
"commands, snapshot update workflow, and PR requirements by reading through README and scripts. A "
"dedicated contributing guide reduces onboarding friction and mismatched expectations.",
[("Category","Documentation"),("Impact Level","Low")],
["Create `CONTRIBUTING.md` at the repository root.",
 "Include: environment setup, building (Rust toolchain, Soroban CLI), running tests, updating snapshots, linting, and PR requirements.",
 "Reference `craft-nexus-contract/README.md` for contract-specific details."])),

dict(title="[DOCS] Document CEI pattern requirements for all public state-mutating functions in a security policy section",
     labels=["documentation","security"],
     body=make_body(
"Soroban CEI pattern compliance is mandatory for all functions that perform token transfers. Currently, "
"CEI compliance is documented in individual code comments but not in a central policy document. This "
"makes it easy for contributors to miss the requirement when adding new transfer-related functions.",
[("Category","Documentation / Security"),("Impact Level","Medium")],
["Add a 'Security Patterns' section to README.",
 "Document the CEI pattern with a before/after code example.",
 "Add a checklist item to the PR template: Does this PR follow CEI ordering for all token transfers?",
 "Reference `SCALABILITY_IMPROVEMENTS.md`'s CEI section for additional context."])),

# ===== TOOLING (73-80) =====================================================

dict(title="[TOOLING] Add cargo-deny or cargo-audit to CI to check for vulnerable cryptographic dependencies",
     labels=["tooling","security"],
     body=make_body(
"The `Cargo.lock` contains many cryptographic dependencies (ed25519-dalek, p256, k256, sha2, etc.). "
"None are audited as part of the CI pipeline. A compromised or vulnerable dependency could undermine "
"the contract's cryptographic guarantees without any automated detection.",
[("Category","Tooling / Security"),("Impact Level","High - undetected vulnerable dependencies")],
["Add `cargo deny check` to the CI workflow.",
 "Add `cargo audit` as a pre-push hook in the repo.",
 "Document which advisory databases are checked.",
 "Set a policy for how long a RUSTSEC advisory is acceptable before a dependency must be updated."])),

dict(title="[TOOLING] scripts/build.sh - add WASM size reporting and MAX_WASM_SIZE_BYTES enforcement",
     labels=["tooling"],
     body=make_body(
"`scripts/build.sh` builds the WASM artifact but does not report its size. On Soroban, WASM binary "
"size directly affects deployment cost. A size regression should fail the build. The script should "
"also apply `wasm-opt` for additional size reduction.",
[("Category","Tooling"),("Impact Level","Medium")],
["After `cargo build --target wasm32-unknown-unknown --release`, add a `wasm-opt` invocation for size reduction.",
 "Print the WASM binary size in bytes.",
 "Add a `MAX_WASM_SIZE_BYTES=65536` check that fails the build if exceeded.",
 "Optionally upload the WASM size to a metrics endpoint for trend tracking."])),

dict(title="[TOOLING] Add `cargo clippy -- -D warnings` to CI to enforce lint cleanliness (79+ current warnings)",
     labels=["tooling"],
     body=make_body(
"`cargo check` currently reports 79-84 warnings across the codebase including: unused variables, "
"unused imports, non-standard constant naming, and dead code. Allowing warnings in CI creates a "
"broken-windows problem where new issues are hidden in the noise.",
[("Category","Tooling"),("Impact Level","Medium")],
["Add `cargo clippy -- -D warnings` as a required CI check.",
 "Resolve all existing warnings (or add targeted `#[allow(...)]` with justification comments for intentional suppressions).",
 "Add the clippy step to `scripts/test.sh`."])),

dict(title="[TOOLING] Add .cargo/config.toml with WASM target configuration and default build flags",
     labels=["tooling"],
     body=make_body(
"The build process requires specific flags for the `wasm32-unknown-unknown` target (e.g., "
"`--no-default-features`, optimization level `z` for size). Currently these flags must be memorized "
"or read from `scripts/build.sh`. A `.cargo/config.toml` would make `cargo build` work correctly "
"without flags, improving contributor experience.",
[("Category","Tooling"),("Impact Level","Low")],
["Create `craft-nexus-contract/.cargo/config.toml`.",
 "Add `[target.wasm32-unknown-unknown]` with `rustflags` for size optimization.",
 "Add `[build]` target defaulting to `wasm32-unknown-unknown` for release builds.",
 "Update `scripts/build.sh` to use the simplified `cargo build --release`."])),

dict(title="[TOOLING] Add GitHub Actions CI workflow for automated testing on every PR",
     labels=["tooling","ci"],
     body=make_body(
"There is no `.github/workflows/` CI configuration in the repository. All testing appears to be done "
"locally. This means: PRs can be merged without passing tests, coverage regressions are invisible, "
"and build errors from different toolchain versions go undetected.",
[("Category","Tooling / CI"),("Impact Level","High - PRs merged without automated verification")],
["Create `.github/workflows/ci.yml` with: `cargo check --tests`, `cargo clippy -- -D warnings`, `cargo test`, and `cargo build --target wasm32-unknown-unknown --release`.",
 "Trigger on `push` and `pull_request` to `main`.",
 "Cache `~/.cargo/registry` and `target/` to speed up builds.",
 "Add a status badge to README."])),

dict(title="[TOOLING] Add Soroban testnet deployment script with environment variable validation",
     labels=["tooling"],
     body=make_body(
"`scripts/deploy.sh` exists but does not validate that required environment variables are set before "
"attempting deployment (STELLAR_SECRET_KEY, NETWORK_PASSPHRASE, RPC_URL), causing cryptic errors when "
"they are missing. `craft-nexus/.env.example` documents these variables.",
[("Category","Tooling"),("Impact Level","Low")],
["Add environment variable validation at the top of `scripts/deploy.sh`.",
 "Print a clear error message if any variable is missing.",
 "Add a `--dry-run` flag that validates the environment without deploying.",
 "Update README Deployment section to reference the `.env.example` file."])),

dict(title="[TOOLING] Add wasm-opt post-processing step to reduce binary size by 20-40%",
     labels=["tooling","performance"],
     body=make_body(
"Stellar Soroban WASM contracts benefit significantly from `wasm-opt` post-processing (-Oz "
"optimization). The Soroban CLI applies optimizations during upload, but running `wasm-opt` locally "
"before upload gives more control and produces smaller artifacts. Smaller WASM means lower upload "
"fees and faster contract execution.",
[("Category","Tooling / Performance"),("Impact Level","Medium")],
["Install `wasm-opt` via `binaryen` in the build environment.",
 "Add `wasm-opt -Oz --output optimized.wasm contract.wasm` to `build.sh`.",
 "Report and compare sizes of the unoptimized and optimized WASM.",
 "Use the optimized WASM for all testnet and mainnet deployments."])),

dict(title="[TOOLING] Add pre-commit hooks for cargo fmt enforcement and snapshot change warnings",
     labels=["tooling"],
     body=make_body(
"There is no enforced code formatting in the repository. Contributors using different Rust versions "
"or IDE settings may introduce formatting diffs that clutter PRs. Snapshot file diffs should also "
"be reviewed before committing to prevent accidental schema regressions.",
[("Category","Tooling"),("Impact Level","Low")],
["Add a `.pre-commit-config.yaml` with: `cargo fmt --check` hook and a custom hook that warns when snapshot files change.",
 "Document the pre-commit setup in CONTRIBUTING.md.",
 "Add `cargo fmt -- --check` to the CI workflow."])),

]  # end ISSUES list

assert len(ISSUES) == 80, f"Expected 80 issues, got {len(ISSUES)}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_labels():
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/labels"
    r = requests.get(url, headers=HEADERS)
    existing = {l["name"] for l in r.json()} if r.ok else set()
    all_labels = set()
    for issue in ISSUES:
        all_labels.update(issue.get("labels", []))
    for label in all_labels:
        if label not in existing:
            color = LABEL_COLORS.get(label, "ededed")
            requests.post(url, headers=HEADERS, json={"name": label, "color": color})
            print(f"  Created label: {label}")

def create_issue(idx, issue):
    url = f"{API_BASE}/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    payload = {"title": issue["title"], "body": issue["body"], "labels": issue.get("labels", [])}
    r = requests.post(url, headers=HEADERS, json=payload)
    if r.ok:
        return True, r.json()["html_url"]
    return False, f"HTTP {r.status_code}: {r.text[:300]}"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if not GITHUB_TOKEN:
        print("ERROR: No GitHub token provided.", file=sys.stderr)
        sys.exit(1)

    me = requests.get(f"{API_BASE}/user", headers=HEADERS)
    if not me.ok:
        print(f"ERROR: Token invalid or missing scope.\n{me.text}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  CraftNexus - GitHub Issue Creator")
    print(f"{'='*60}")
    print(f"  Authenticated as : {me.json()['login']}")
    print(f"  Target repo      : {REPO_OWNER}/{REPO_NAME}")
    print(f"  Issues to create : {len(ISSUES)}")
    print(f"{'='*60}\n")

    print("Ensuring labels exist...")
    ensure_labels()
    print("Labels ready.\n")

    created, failed = [], []

    for i, issue in enumerate(ISSUES, 1):
        ok, result = create_issue(i, issue)
        if ok:
            created.append((i, result))
            print(f"  [{i:02d}/80] OK  {issue['title'][:68]}")
        else:
            failed.append((i, issue["title"], result))
            print(f"  [{i:02d}/80] ERR {result}")
        time.sleep(1.1)   # respect GitHub secondary rate limits

    print(f"\n{'='*60}")
    print(f"  DONE: {len(created)} created  |  {len(failed)} failed")
    print(f"{'='*60}")

    if created:
        print(f"\n  First: {created[0][1]}")
        print(f"  Last : {created[-1][1]}")

    if failed:
        print(f"\nFailed issues:")
        for num, title, err in failed:
            print(f"  #{num:02d}: {title[:60]}")
            print(f"        {err}")

if __name__ == "__main__":
    main()
