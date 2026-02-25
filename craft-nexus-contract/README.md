# CraftNexus Escrow Smart Contract

Stellar Smart Contract (Soroban) for secure escrow payments on CraftNexus.

## Overview

This contract handles escrow functionality for marketplace transactions:
- Secure payment holding for physical goods
- Automatic release after delivery window
- Buyer-controlled release
- Refund functionality for disputes

## Prerequisites

- Rust 1.70.0 or later
- Stellar Soroban CLI
- Stellar account with testnet XLM (for deployment)

## Installation

### Install Stellar CLI

```bash
cargo install --locked stellar-cli
```

### Install Rust Target

```bash
rustup target add wasm32-unknown-unknown
```

## Building the Contract

```bash
cd craft-nexus-contract
stellar contract build
```

This will create a WASM file in `target/wasm32-unknown-unknown/release/craft_nexus_contract.wasm`

## Deployment

### Prerequisites

- [Stellar CLI](https://developers.stellar.org/docs/build/smart-contracts/getting-started/setup#install-the-stellar-cli) installed.
- A Stellar account with testnet/mainnet funds.

### Required Secrets

To deploy the contract, you will need:
- **Source Account Secret Key**: The private key of the account that will deploy and pay for the contract. Keep this secret!

### Automated Deployment (Recommended)

A deployment script is provided in the frontend repository to simplify the process.

```bash
# From the craft-nexus (frontend) directory
./scripts/deploy-contract.sh [testnet|mainnet] <YOUR_SECRET_KEY>
```

The script will:
1. Build the contract.
2. Deploy the WASM to the specified network.
3. Output the new Contract ID.
4. Provide the environment variable entry for the frontend.

### Manual Deployment

#### 1. Setup Network

**Testnet:**
```bash
stellar network add --rpc-url https://soroban-testnet.stellar.org:443 --network-passphrase "Test SDF Network ; September 2015" testnet
```

**Mainnet:**
```bash
stellar network add --rpc-url https://soroban-rpc.mainnet.stellar.org:443 --network-passphrase "Public Global Stellar Network ; September 2015" mainnet
```

#### 2. Build and Deploy

```bash
# Build
stellar contract build

# Deploy
stellar contract deploy \
  --wasm target/wasm32-unknown-unknown/release/craft_nexus_contract.wasm \
  --source <YOUR_IDENTITY_NAME_OR_SECRET_KEY> \
  --network testnet
```

#### 3. Update Environment Variables

After deployment, copy the returned Contract ID and add it to your frontend `.env.local`:

```
NEXT_PUBLIC_ESCROW_CONTRACT_ADDRESS=<CONTRACT_ID>
```

## Initialization

After deployment, you must initialize an escrow (this is typically done by the frontend application):

```bash
stellar contract invoke \
  --id <CONTRACT_ID> \
  --source <YOUR_IDENTITY_NAME_OR_SECRET_KEY> \
  --network testnet \
  -- \
  create_escrow \
  --buyer <BUYER_ADDRESS> \
  --seller <SELLER_ADDRESS> \
  --token <USDC_TOKEN_ADDRESS> \
  --amount 1000000000 \
  --order_id 1 \
  --release_window 604800
```

## Contract Functions

### `create_escrow`
Create a new escrow for an order.

**Parameters:**
- `buyer`: Buyer's Stellar address
- `seller`: Seller's Stellar address  
- `token`: Token contract address (USDC)
- `amount`: Amount in stroops (1 USDC = 10,000,000 stroops)
- `order_id`: Unique order identifier
- `release_window`: Time in seconds before auto-release (default: 604800 = 7 days)

### `release_funds`
Release funds to seller (called by buyer after delivery confirmation).

**Parameters:**
- `order_id`: Order identifier

### `auto_release`
Auto-release funds after release window (seller can call).

**Parameters:**
- `order_id`: Order identifier

### `refund`
Refund funds to buyer (for disputes).

**Parameters:**
- `order_id`: Order identifier
- `authorized_address`: Address authorized to refund

### `get_escrow`
Get escrow details.

**Parameters:**
- `order_id`: Order identifier

### `can_auto_release`
Check if escrow can be auto-released.

**Parameters:**
- `order_id`: Order identifier

## Integration

See `craft-nexus/lib/stellar/contracts.ts` for TypeScript integration examples.

## Contract Address

- **Testnet**: `[DEPLOY_AND_UPDATE]`
- **Mainnet**: `[DEPLOY_AND_UPDATE]`
