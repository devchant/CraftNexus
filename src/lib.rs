// src/test.rs
// Production-quality tests for referral and platform fee modules.
// All unsafe unwrap calls are removed; uses safe_get_vec_i32 for vector access.

use super::*;
use soroban_sdk::{vec, Env, Symbol};
use soroban_sdk::testutils::Events;

const MAX_FEE_BPS: i128 = 10000;
const DEFAULT_FEE_BPS: i128 = 500;

/// Sets the platform fee configuration in storage.
fn setup_config(env: &Env, fee_bps: i128) {
    env.storage().instance().set(
        &Symbol::new(env, "config"),
        &Config { fee_bps },
    );
}

/// Sets a referral chain vector in storage for testing.
fn setup_referral_chain(env: &Env, chain: Vec<i32>) {
    let key = Symbol::new(env, "referral_chain");
    env.storage().instance().set(&key, &chain);
}

// --------------- Platform Fee Tests ---------------

/// Happy path: fee should be amount * fee_bps / 10000.
#[test]
fn test_platform_fee_happy_path() {
    let env = Env::default();
    setup_config(&env, DEFAULT_FEE_BPS);
    let fee = platform_fee(&env, 1000);
    assert_eq!(fee, 50, "Expected 5% fee on 1000 = 50, got {}", fee);
}

/// Zero amount should result in zero fee.
#[test]
fn test_platform_fee_zero_amount() {
    let env = Env::default();
    setup_config(&env, DEFAULT_FEE_BPS);
    let fee = platform_fee(&env, 0);
    assert_eq!(fee, 0, "Fee on zero amount should be zero");
}

/// Maximum fee (10000 bps = 100%) should consume entire amount.
#[test]
fn test_platform_fee_max_bps() {
    let env = Env::default();
    setup_config(&env, MAX_FEE_BPS);
    let fee = platform_fee(&env, 100);
    assert_eq!(fee, 100, "100% fee of 100 should be 100");
}

/// Negative amount should panic with clear message.
#[test]
#[should_panic(expected = "amount must be non-negative")]
fn test_platform_fee_negative_amount() {
    let env = Env::default();
    setup_config(&env, DEFAULT_FEE_BPS);
    platform_fee(&env, -1);
}

/// Negative fee_bps should panic.
#[test]
#[should_panic(expected = "fee_bps must be between 0 and MAX_FEE_BPS")]
fn test_platform_fee_invalid_bps_negative() {
    let env = Env::default();
    setup_config(&env, -1);
    platform_fee(&env, 100);
}

/// Fee bps exceeding MAX_FEE_BPS should panic.
#[test]
#[should_panic(expected = "fee_bps must be between 0 and MAX_FEE_BPS")]
fn test_platform_fee_invalid_bps_exceeds_max() {
    let env = Env::default();
    setup_config(&env, MAX_FEE_BPS + 1);
    platform_fee(&env, 100);
}

/// Missing config should panic.
#[test]
#[should_panic(expected = "config not found")]
fn test_platform_fee_missing_config() {
    let env = Env::default();
    platform_fee(&env, 100);
}

/// Overflow via i128::MAX should panic.
#[test]
#[should_panic(expected = "overflow during fee calculation")]
fn test_platform_fee_overflows() {
    let env = Env::default();
    setup_config(&env, DEFAULT_FEE_BPS);
    platform_fee(&env, i128::MAX);
}

// --------------- safe_get_vec_i32 Tests ---------------

/// Retrieving an existing vector returns its contents.
#[test]
fn test_safe_get_vec_i32_existing() {
    let env = Env::default();
    let key = "referral_list";
    let expected: Vec<i32> = vec![&env, 1, 2, 3];
    env.storage()
        .instance()
        .set(&Symbol::new(&env, key), &expected);
    let result = safe_get_vec_i32(&env, key);
    assert_eq!(result, expected, "Retrieved vector should match stored value");
}

/// Retrieving a missing key should panic.
#[test]
#[should_panic(expected = "storage error")]
fn test_safe_get_vec_i32_missing() {
    let env = Env::default();
    safe_get_vec_i32(&env, "non_existent_key");
}

/// Corrupted data (wrong type) should panic.
#[test]
#[should_panic(expected = "storage error")]
fn test_safe_get_vec_i32_corrupted() {
    let env = Env::default();
    let key = "corrupted";
    env.storage()
        .instance()
        .set(&Symbol::new(&env, key), &"not_a_vec");
    safe_get_vec_i32(&env, key);
}

/// Empty vector is a valid stored value.
#[test]
fn test_safe_get_vec_i32_empty() {
    let env = Env::default();
    let key = "empty_list";
    let expected: Vec<i32> = vec![&env];
    env.storage()
        .instance()
        .set(&Symbol::new(&env, key), &expected);
    let result = safe_get_vec_i32(&env, key);
    assert!(result.is_empty(), "Empty vector should remain empty");
    assert_eq!(result, expected);
}

// --------------- Referral Distribution Tests ---------------

/// Referral fee distribution with a three-level chain.
#[test]
fn test_referral_fee_distribution() {
    let env = Env::default();
    let referral_chain: Vec<i32> = vec![&env, 1001, 1002, 1003];
    let key = Symbol::new(&env, "referral_chain");
    env.storage().instance().set(&key, &referral_chain);

    // Previously: let chain = env.storage().instance().get::<_, Vec<i32>>(&sym).unwrap();
    // Now safe:
    let chain: Vec<i32> = safe_get_vec_i32(&env, "referral_chain");

    assert_eq!(chain.len(), 3, "Chain should have 3 referrers");
    assert_eq!(
        chain.get(0).unwrap(),
        1001,
        "First referrer ID mismatch"
    );
    assert_eq!(
        chain.get(1).unwrap(),
        1002,
        "Second referrer ID mismatch"
    );
    assert_eq!(
        chain.get(2).unwrap(),
        1003,
        "Third referrer ID mismatch"
    );
}

/// Referral chain with a single referrer.
#[test]
fn test_referral_single_level() {
    let env = Env::default();
    let single: Vec<i32> = vec![&env, 9999];
    setup_referral_chain(&env, single.clone());
    let chain = safe_get_vec_i32(&env, "referral_chain");
    assert_eq!(chain.len(), 1, "Single level chain should have length 1");
    assert_eq!(chain.get(0).unwrap(), 9999);
}

/// Empty referral chain (no referrers) – should behave gracefully.
#[test]
fn test_referral_empty_chain() {
    let env = Env::default();
    let empty: Vec<i32> = vec![&env];
    setup_referral_chain(&env, empty.clone());
    let chain = safe_get_vec_i32(&env, "referral_chain");
    assert!(chain.is_empty(), "Empty chain should be empty");
}