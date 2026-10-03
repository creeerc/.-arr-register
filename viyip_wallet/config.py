"""Configuration for the Viyip digital wallet app."""

import os

# Base directory for app data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "wallet.db")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Viyip payment system configuration
# In production these would be real API keys/endpoints.
VIYIP_API_BASE = "https://api.viyip.example.com/v1"
VIYIP_API_KEY = "sk_live_viyip_demo_key_0000"
VIYIP_MERCHANT_ID = "merch_viyip_demo_0000"

# Viyip fee schedule (percentages of transaction amount)
VIYIP_FEES = {
    "transfer": 0.015,   # 1.5% for P2P transfer
    "payment": 0.02,     # 2.0% for merchant payment
    "add_money": 0.01,   # 1.0% for adding money via card/netbanking
}

# Flat fee caps
VIYIP_MAX_FEE = 500.0  # max fee per transaction
VIYIP_MIN_FEE = 1.0    # min fee per transaction

# Supported payment methods
PAYMENT_METHODS = ["card", "netbanking", "upi", "wallet", "viyip"]

# Default currency
CURRENCY = "INR"

# App metadata
APP_NAME = "Viyip Wallet"
APP_VERSION = "1.0.0"