# RPCfi Flow Simulator - Avalanche

A professional Streamlit application that simulates RPCfi revenue flows, buybacks, LP growth, and developer yield for the Avalanche blockchain with NEURA token integration.

## Features

- **About RPCfi Page**: Comprehensive explanation of RPCfi concept and mechanics
- **Avalanche Focused**: Dedicated simulation for AVAX/NEURA token pair
- **APY Scenarios**: Three distinct scenarios (20%, 30%, 40% APY)
- **2-Year Projection**: Extended simulation from Jan 2026 to Dec 2027
- **Professional Design**: Clean, sober interface with pastel colors
- **Comprehensive Analytics**: Detailed charts and tables showing buyback flows, LP growth, and yield distribution
- **Historical Data Integration**: Built-in historical revenue data for accurate projections

## Overview

The RPCfi Flow Simulator models how RPC revenue is distributed through the ecosystem:

1. **RPC Revenue** → 50% used for buybacks (25% AVAX, 25% NEURA), 50% to Ankr protocol
2. **Buybacks** → Create LP tokens on Neura blockchain
3. **LP Tokens** → Generate yield through NEURA emissions
4. **Yield Distribution** → Rewards developers and foundations

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project files**

2. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv rpcfi_env
   .\rpcfi_env\Scripts\Activate.ps1
   
   # macOS/Linux
   python -m venv rpcfi_env
   source rpcfi_env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```

2. **Select APY scenario** from the dropdown (Worst, Base, or Best case)

3. **Run simulation** and explore results across three tabs:
   - **Overview**: Summary metrics and APY scenario selection
   - **Buyback & LP Flows**: Weekly buybacks and LP TVL growth
   - **Yield & Revenue**: Developer and foundation yield distribution

### Logo Setup

Replace the placeholder logo files with actual images:
- `avax.png` - Avalanche logo
- `neura.png` - NEURA token logo

### Configuration

The simulator uses a single configuration file (`config_avax.json`) with the following structure:

```json
{
  "chain_name": "Avalanche",
  "native_token": "AVAX",
  "governance_token": "NEURA",
  "token_prices": {
    "AVAX": 25.0,
    "NEURA": 0.80
  },
  "initial_lp": {
    "Avalanche Foundation": 50000,
    "Neura Foundation": 50000
  },
  "growth_multiplier": 1.4,
  "expected_future_growth_multiplier": 2.0,
  "apy_scenarios": {
    "worst": 20.0,
    "base": 30.0,
    "best": 40.0
  },
  "historical_data": {
    "2025-04": 15000.0,
    "2025-05": 18000.0,
    "2025-06": 22000.0,
    "2025-07": 25000.0,
    "2025-08": 30000.0,
    "2025-09": 35000.0
  }
}
```

### Helper Script

Generate synthetic revenue data using the helper script:

```bash
# Generate moderate scenario data
python simulate_rpcfi.py --scenario moderate

# Generate all scenarios
python simulate_rpcfi.py --scenario all

# Create sample configuration files
python simulate_rpcfi.py --create-configs
```

## 📊 Simulation Logic

### Revenue Split
- **25%** → Native token buybacks (e.g., TRX)
- **25%** → ANKR buybacks
- **50%** → Ankr protocol (not simulated)

### LP Creation
- Buyback funds purchase tokens at configured prices
- Tokens paired 1:1 value-wise to create LP tokens
- LP tokens earn NEURA emissions

### Yield Calculation
- **Foundation LPs**: Static $50k per foundation
- **Developer LPs**: Accumulated from weekly buybacks
- **APY**: Configurable base rates with veBoost multipliers
- **Weekly yield**: `LP_value * (APY / 52)`

### Growth Modeling
- **Immediate growth**: Applied at simulation start
- **Future growth**: Linear interpolation to target multiplier
- **Revenue adjustment**: `base_revenue * growth_multiplier * future_curve`

## 📁 File Structure

```
Rpcfi/
├── app.py                    # Main Streamlit application
├── simulate_rpcfi.py         # Helper script for data generation
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── config_template.json     # Configuration template
├── config_tron.json         # Tron chain configuration
├── config_bnb.json          # BNB chain configuration
├── config_polygon.json      # Polygon chain configuration
└── rpcfi_env/              # Virtual environment (created during setup)
```

## 🔧 Customization

### Adding New Chains

1. Create a new configuration file (e.g., `config_ethereum.json`)
2. Set appropriate token prices, growth multipliers, and APY settings
3. The application will automatically detect and load the new configuration

### Modifying Simulation Logic

Edit the `RPCfiSimulator` class in `app.py` to:
- Adjust revenue split ratios
- Modify growth curve algorithms
- Change yield calculation methods
- Add new metrics or visualizations

## 📈 Example Outputs

The simulator provides comprehensive analytics including:

- **Total RPC Revenue**: Sum of all monthly revenue
- **Total Buybacks**: Combined TRX and ANKR buyback amounts
- **Final LP TVL**: Total liquidity pool value
- **Developer Yield**: Cumulative yield distributed to developers
- **Foundation Yield**: Yield earned by foundations
- **Growth Metrics**: Revenue growth over time

## 🤝 Contributing

To contribute to the RPCfi Flow Simulator:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For questions or issues:

1. Check the configuration files for proper formatting
2. Ensure all dependencies are installed correctly
3. Verify Python version compatibility (3.8+)
4. Review the simulation logic in the code comments

## 🔮 Future Enhancements

Potential improvements for future versions:

- Real-time price feeds integration
- Advanced growth curve modeling
- Risk analysis and scenario planning
- Export functionality for results
- Multi-chain comparison views
- Historical data integration
- Advanced yield optimization strategies
