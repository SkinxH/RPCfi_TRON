# RPCfi Flow Simulator - Tron Instructions

## Overview

This application simulates RPCfi revenue flows for the Tron blockchain, focusing on TRX/ANKR token pairs and conservative revenue modeling without growth assumptions.

## Key Changes from Avalanche Version

### 1. Token Focus
- **Native Token**: Changed from AVAX to TRX
- **LP Pairs**: Now uses TRX/ANKR instead of AVAX/NEURA (original)
- **Token Prices**: Updated to reflect TRX pricing (~$0.12)

### 2. Revenue Model
- **No Growth Assumptions**: Removed all hardcoded growth projections
- **Flat Revenue**: Uses last historical month as constant baseline
- **Conservative Approach**: Focuses on current revenue levels

### 3. Configuration
- **Config File**: `config_tron.json` (renamed from `config_avax.json`)
- **Chain Name**: Updated to "Tron"
- **Foundation**: Changed to "Tron Foundation"

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv rpcfi_env

# Activate environment
# Windows:
.\rpcfi_env\Scripts\Activate.ps1
# macOS/Linux:
source rpcfi_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration
- Update `config_tron.json` with current TRX and ANKR prices
- Adjust APY scenarios as needed
- Modify historical revenue data if available

### 3. Logo Setup
- Replace `avax.png` with `trx.png` (Tron logo)
- Ensure `neura.png` is present

### 4. Running the Application
```bash
streamlit run app.py
```

## Revenue Model Details

### Flat Revenue Approach
- Uses the last historical month's revenue as a constant baseline
- No growth projections or assumptions
- Conservative modeling focused on current reality

### Revenue Split
- **50%** → Ankr protocol (infrastructure costs)
- **25%** → TRX buybacks
- **25%** → ANKR buybacks

### LP Creation
- Buyback funds purchase TRX and ANKR tokens
- Tokens are paired 1:1 value-wise to create LP tokens
- LP tokens earn yield through ANKR emissions

## Key Features

1. **Conservative Modeling**: No speculative growth assumptions
2. **Tron Integration**: Full TRX/ANKR token pair support
3. **Flat Revenue**: Uses historical data as constant baseline
4. **APY Scenarios**: Configurable yield scenarios (20%, 30%, 40%)
5. **Professional UI**: Clean interface with Tron branding

## Customization

### Modifying Token Prices
Update the `token_prices` section in `config_tron.json`:
```json
"token_prices": {
  "TRX": 0.12,
  "ANKR": 0.025
}
```

### Adjusting APY Scenarios
Modify the `apy_scenarios` section:
```json
"apy_scenarios": {
  "worst": 20.0,
  "base": 30.0,
  "best": 40.0
}
```

### Historical Data
Update the `historical_data` section with actual revenue data:
```json
"historical_data": {
  "2025-04": 22995.0,
  "2025-05": 34291.31,
  "2025-06": 28310.05,
  "2025-07": 20118.68,
  "2025-08": 52151.98,
  "2025-09": 23876.74
}
```

## Troubleshooting

### Common Issues
1. **Missing Logo**: Ensure `trx.png` and `neura.png` are in the directory
2. **Config Error**: Check `config_tron.json` syntax
3. **Dependencies**: Run `pip install -r requirements.txt`

### File Structure
```
RPCFi/
├── app.py                    # Main application
├── config_tron.json         # Tron configuration
├── simulate_rpcfi.py        # Data generation script
├── requirements.txt         # Dependencies
├── trx.png                  # Tron logo
├── ankr.png                # ANKR logo
├── rpcfi.png               # RPCfi logo
└── README.md               # Documentation
```

## Support

For issues or questions:
1. Check configuration file syntax
2. Verify all dependencies are installed
3. Ensure logo files are present
4. Review the simulation logic in the code comments
