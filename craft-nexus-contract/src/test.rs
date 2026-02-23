#![cfg(test)]

use super::*;
use soroban_sdk::{testutils::{Address as _, Ledger}, Address, Env, token};

fn setup_test(env: &Env) -> (EscrowContractClient<'static>, Address, Address, Address, token::StellarAssetClient<'static>) {
    let contract_id = env.register_contract(None, EscrowContract);
    let client = EscrowContractClient::new(env, &contract_id);

    let buyer = Address::generate(env);
    let seller = Address::generate(env);
    
    let token_admin = Address::generate(env);
    let token_id = env.register_stellar_asset_contract(token_admin.clone());
    let token_admin_client = token::StellarAssetClient::new(env, &token_id);

    (client, buyer, seller, token_id, token_admin_client)
}

#[test]
fn test_create_escrow_success() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    
    let order_id = 1;
    let amount = 500;
    let window = 3600;
    
    let escrow = client.create_escrow(&buyer, &seller, &token_id, &amount, &order_id, &Some(window));
    
    assert_eq!(escrow.buyer, buyer);
    assert_eq!(escrow.seller, seller);
    assert_eq!(escrow.amount, amount);
    assert_eq!(escrow.status, EscrowStatus::Pending);
    assert_eq!(escrow.release_window, window);
    
    let stored_escrow = client.get_escrow(&order_id);
    assert_eq!(stored_escrow, escrow);
}

#[test]
fn test_create_escrow_default_window() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    let escrow = client.create_escrow(&buyer, &seller, &token_id, &500, &1, &None);
    
    assert_eq!(escrow.release_window, 604800); // 7 days
}

#[test]
fn test_release_funds_success() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &None);
    
    client.release_funds(&1);
    
    let escrow = client.get_escrow(&1);
    assert_eq!(escrow.status, EscrowStatus::Released);
    
    let token_client = token::Client::new(&env, &token_id);
    assert_eq!(token_client.balance(&seller), 500);
    assert_eq!(token_client.balance(&client.address), 0);
}

#[test]
#[should_panic(expected = "Escrow already processed")]
fn test_release_funds_already_processed() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &None);
    client.release_funds(&1);
    client.release_funds(&1); // Should panic
}

#[test]
fn test_auto_release_success_after_window() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    let window = 100;
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &Some(window));
    
    // Advance time
    env.ledger().with_mut(|li| {
        li.timestamp += window + 1;
    });
    
    assert!(client.can_auto_release(&1));
    client.auto_release(&1);
    
    let escrow = client.get_escrow(&1);
    assert_eq!(escrow.status, EscrowStatus::Released);
    
    let token_client = token::Client::new(&env, &token_id);
    assert_eq!(token_client.balance(&seller), 500);
}

#[test]
#[should_panic(expected = "Release window not yet elapsed")]
fn test_auto_release_failure_before_window() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &Some(100));
    
    assert!(!client.can_auto_release(&1));
    client.auto_release(&1);
}

#[test]
fn test_refund_success_by_buyer() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &None);
    
    client.refund(&1, &buyer);
    
    let escrow = client.get_escrow(&1);
    assert_eq!(escrow.status, EscrowStatus::Refunded);
    
    let token_client = token::Client::new(&env, &token_id);
    assert_eq!(token_client.balance(&buyer), 1000);
}

#[test]
#[should_panic(expected = "Not authorized to refund")]
fn test_refund_failure_unauthorized() {
    let env = Env::default();
    env.mock_all_auths();
    let (client, buyer, seller, token_id, token_admin) = setup_test(&env);
    
    token_admin.mint(&buyer, &1000);
    client.create_escrow(&buyer, &seller, &token_id, &500, &1, &None);
    
    let unauthorized = Address::generate(&env);
    client.refund(&1, &unauthorized);
}

#[test]
#[should_panic(expected = "Escrow not found")]
fn test_get_escrow_not_found() {
    let env = Env::default();
    let (client, _, _, _, _) = setup_test(&env);
    client.get_escrow(&999);
}
