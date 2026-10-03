# Viyip Wallet

A digital wallet Linux desktop app built with Python + Tkinter, integrating the
**Viyip payment system** for transaction payments, money transfers, adding money,
and merchant payments.

## Features

- **Sign up / Login** with email + password (SHA-256 hashed)
- **Send money / transfer** to any Viyip consumer account (1.5% Viyip fee)
- **Merchant payments** via the Viyip payment system (2% Viyip fee)
- **Add money** from card / netbanking / UPI / wallet (1% Viyip fee)
- **Transaction history** with Viyip fee summary
- **Pricing & fee calculation** per transaction type with caps
- SQLite-backed persistent storage

## Project Structure

```
viyip_wallet/
├── config.py            # App config, Viyip API keys, fee schedule
├── database.py          # SQLite schema + CRUD
├── viyip_gateway.py     # Viyip payment system client (charge/transfer/add_money)
├── wallet_service.py    # Orchestrates gateway + DB
├── app.py               # Tkinter root + screen navigation
├── main.py              # Entry point
├── ui/
│   ├── styles.py        # Theme
│   ├── base.py          # Reusable widgets
│   └── screens/         # Welcome, Login, Signup, Dashboard, Transfer,
│                        #   Add Money, Payment, History
├── test_wallet.py       # Headless smoke tests
└── data/                # wallet.db created at runtime
```

## Fee Schedule (Viyip)

| Operation      | Fee        |
|----------------|------------|
| Transfer       | 1.5%       |
| Payment        | 2.0%       |
| Add Money      | 1.0%       |
| Min / Max cap  | ₹1 / ₹500  |

## Running

```bash
# Install tkinter (Linux)
sudo apt-get install python3-tk

# Run the app
python3 main.py
```

## Testing (headless)

```bash
python3 test_wallet.py
```

## Notes

- The Viyip gateway is a simulated in-process client so the app runs fully
  offline. Point `VIYIP_API_BASE` / `VIYIP_API_KEY` in `config.py` to talk to
  the live Viyip REST API.
- All secrets are hashed at rest; never commit real API keys.