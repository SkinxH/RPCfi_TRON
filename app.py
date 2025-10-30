import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import yaml
from datetime import datetime, timedelta
import os
from typing import Dict, List, Tuple

# Page configuration
st.set_page_config(
    page_title="RPCfi Flow Simulator",
    page_icon="trx.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 5rem;
        font-weight: 300;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0.75rem 1.5rem;
        font-size: 1.5rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #e74c3c;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class RPCfiSimulator:
    def __init__(self, config: Dict):
        self.config = config
        self.chain_name = config['chain_name']
        self.native_token = config['native_token']
        self.governance_token = config['governance_token']
        self.token_prices = config['token_prices']
        self.initial_lp = config['initial_lp']
        self.growth_multiplier = config['growth_multiplier']
        self.expected_future_growth_multiplier = config['expected_future_growth_multiplier']
        self.apy_scenarios = config.get('apy_scenarios', {
            'worst': 20.0,
            'base': 30.0,
            'best': 40.0
        })
        self.historical_data = config.get('historical_data', {})
        
        # Initialize simulation data
        self.simulation_data = None
        self.weekly_data = None
        
    def load_revenue_data(self, revenue_data: Dict[str, float]) -> pd.DataFrame:
        """Load and process monthly revenue data"""
        df = pd.DataFrame(list(revenue_data.items()), columns=['Month', 'RPC_Revenue_USD'])
        df['Month'] = pd.to_datetime(df['Month'])
        df = df.sort_values('Month')
        
        # Convert monthly to weekly data
        weekly_data = []
        for _, row in df.iterrows():
            monthly_revenue = row['RPC_Revenue_USD']
            weekly_revenue = monthly_revenue / 4.33  # Approximate weeks per month
            
            # Generate 4 weeks for each month
            for week in range(4):
                week_date = row['Month'] + timedelta(weeks=week)
                weekly_data.append({
                    'Date': week_date,
                    'RPC_Revenue_USD': weekly_revenue
                })
        
        return pd.DataFrame(weekly_data)
    
    
    def calculate_buybacks(self, weekly_revenue: float) -> Tuple[float, float]:
        """Calculate TRX and ANKR buybacks from weekly revenue (50% of revenue used)"""
        # Only 50% of revenue is used for buybacks
        buyback_pool = 0.50 * weekly_revenue
        # Split the 50% equally between TRX and ANKR
        trx_buyback = 0.25 * weekly_revenue  # 25% of total revenue
        ankr_buyback = 0.25 * weekly_revenue  # 25% of total revenue
        return trx_buyback, ankr_buyback
    
    def calculate_lp_units(self, trx_buyback: float, ankr_buyback: float) -> Tuple[float, float]:
        """Calculate LP units from buyback amounts"""
        trx_price = self.token_prices[self.native_token]
        ankr_price = self.token_prices[self.governance_token]
        
        trx_units = trx_buyback / trx_price
        ankr_units = ankr_buyback / ankr_price
        
        return trx_units, ankr_units
    
    def calculate_lp_value(self, trx_units: float, ankr_units: float) -> float:
        """Calculate LP value in USD"""
        trx_price = self.token_prices[self.native_token]
        ankr_price = self.token_prices[self.governance_token]
        
        # LP value is the total value of both tokens in the pair
        return trx_units * trx_price + ankr_units * ankr_price
    
    def calculate_yield(self, lp_value: float, apy: float) -> float:
        """Calculate weekly yield from LP value"""
        weekly_yield = lp_value * (apy / 100) / 52
        return weekly_yield
    
    def generate_future_revenue_data(self) -> Dict[str, float]:
        """Generate future monthly revenue data using modular growth assumptions."""
        # Read simulation period from config (fallback to 2026-2027)
        sim_period = self.config.get('simulation_period', {})
        start_str = sim_period.get('start', '2026-01-01')
        end_str = sim_period.get('end', '2027-12-31')
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')

        # Base revenue: last historical month, scaled by initial growth multiplier
        if self.historical_data:
            last_month_revenue = list(self.historical_data.values())[-1]
        else:
            last_month_revenue = 35000.0
        base_revenue = last_month_revenue * self.growth_multiplier

        revenue_data = {}
        current_date = start_date

        # Linear ramp from 1.0 to expected_future_growth_multiplier over the period
        while current_date <= end_date:
            months_elapsed = (current_date.year - start_date.year) * 12 + (current_date.month - start_date.month)
            total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            if total_months > 0:
                growth_factor = 1.0 + (self.expected_future_growth_multiplier - 1.0) * (months_elapsed / total_months)
            else:
                growth_factor = 1.0

            monthly_revenue = base_revenue * growth_factor
            month_key = current_date.strftime('%Y-%m')
            revenue_data[month_key] = monthly_revenue

            # Next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)

        return revenue_data
    
    
    def run_simulation(self, apy_scenario: str = 'base') -> pd.DataFrame:
        """Run the complete simulation"""
        # Generate future revenue data
        revenue_data = self.generate_future_revenue_data()
        
        # Load and process revenue data
        weekly_df = self.load_revenue_data(revenue_data)
        total_weeks = len(weekly_df)
        
        # Get APY for selected scenario
        apy = self.apy_scenarios[apy_scenario]
        
        # Initialize simulation results
        results = []
        cumulative_dev_lp = 0
        cumulative_dev_yield = 0
        cumulative_foundation_yield = 0
        
        # Foundation LP values
        foundation_lp_value = sum(self.initial_lp.values())
        
        for week_num, (_, row) in enumerate(weekly_df.iterrows()):
            # Use the revenue directly (growth already applied at monthly level)
            weekly_revenue = row['RPC_Revenue_USD']
            
            # Calculate buybacks from current week's revenue
            trx_buyback, ankr_buyback = self.calculate_buybacks(weekly_revenue)
            
            # Calculate LP units and value from this week's buybacks
            trx_units, ankr_units = self.calculate_lp_units(trx_buyback, ankr_buyback)
            weekly_lp_value = self.calculate_lp_value(trx_units, ankr_units)
            
            # Update cumulative developer LP (only grows from new deposits, no compounding)
            cumulative_dev_lp += weekly_lp_value
            
            # Calculate yields based on current LP values (yield doesn't compound into LP)
            dev_yield = self.calculate_yield(cumulative_dev_lp, apy)
            foundation_yield = self.calculate_yield(foundation_lp_value, apy)
            
            # Update cumulative yields (yields are paid out, not reinvested)
            cumulative_dev_yield += dev_yield
            cumulative_foundation_yield += foundation_yield
            
            # Store results
            results.append({
                'Date': row['Date'],
                'Week': week_num + 1,
                'RPC_Revenue_USD': weekly_revenue,
                'TRX_Buyback_USD': trx_buyback,
                'ANKR_Buyback_USD': ankr_buyback,
                'TRX_Units': trx_units,
                'ANKR_Units': ankr_units,
                'Weekly_LP_Value_USD': weekly_lp_value,
                'Cumulative_RPCfi_LP_USD': cumulative_dev_lp,
                'Total_LP_TVL_USD': cumulative_dev_lp + foundation_lp_value,
                'Dev_Weekly_Yield_USD': dev_yield,
                'Foundation_Weekly_Yield_USD': foundation_yield,
                'Cumulative_Dev_Yield_USD': cumulative_dev_yield,
                'Cumulative_Foundation_Yield_USD': cumulative_foundation_yield
            })
        
        self.simulation_data = pd.DataFrame(results)
        return self.simulation_data

def load_config(config_file: str) -> Dict:
    """Load configuration from JSON or YAML file"""
    try:
        with open(config_file, 'r') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except FileNotFoundError:
        st.error(f"Config file {config_file} not found!")
        return None
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return None

def get_default_revenue_data() -> Dict[str, float]:
    """Get default revenue data for demonstration"""
    return {
        "2025-04": 15000.0,
        "2025-05": 18000.0,
        "2025-06": 22000.0,
        "2025-07": 25000.0,
        "2025-08": 30000.0,
        "2025-09": 35000.0
    }

def main():
    # Load Tron configuration
    config = load_config('config_tron.json')
    if config is None:
        st.error("Configuration file not found!")
        return
    
    # Main header with logos - better positioning
    col1, col2, col3 = st.columns([0.8, 2.4, 0.8])
    
    with col1:
        if os.path.exists('trx.png'):
            st.image('trx.png', width=50)
    
    with col2:
        st.markdown('<div class="main-header">RPCfi Flow Simulator</div>', unsafe_allow_html=True)
    
    with col3:
        if os.path.exists('ankr.png'):
            st.image('ankr.png', width=50)
    
    # Initialize simulator
    simulator = RPCfiSimulator(config)
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["About RPCfi", "Overview", "Buyback & LP Flows", "Yield & Revenue"])
    
    with tab1:
        show_about_page(simulator)
    
    with tab2:
        show_overview_page(simulator)
    
    with tab3:
        show_buyback_page(simulator)
    
    with tab4:
        show_yield_page(simulator)

def show_about_page(simulator: RPCfiSimulator):
    """Display the About RPCfi page"""
    st.header("About RPCfi")
    
    # RPCfi logo if available
    if os.path.exists('rpcfi.png'):
        st.image('rpcfi.png', width=1000)
    
    st.markdown("""
    ## How RPCfi Aims to Revive DeFi Yield
    
    The last cycle taught DeFi protocol builders a hard lesson: incentive emissions pump charts, then drain treasuries and trust. 
    Total value locked still appears large on dashboards, but headline TVL near the $150 billion mark masks fragile retention 
    and cyclical outflows as farmers chase higher APRs elsewhere. The result is a growth engine that sputters whenever token rewards thin out.
    
    Industry leaders have warned about this loop for years. The well-worn playbook includes shipping a token, spraying incentives 
    to boost TVL, celebrating the spike and then watching capital rotate away. It creates surface-level momentum without durable value. 
    The model invites mercenary liquidity and leaves communities with overhangs and weak fundamentals.
    
    **Sustainable yield comes from services that people actually use and pay for**: blockspace, liquidity provision, security, 
    compute and data access. Fees tied to real utility are modest, but they scale with usage and they compound. The question 
    DeFi has wrestled with is where to find more of these "real economy" revenue streams that don't rely on continual token issuance.
    """)
    
    st.markdown("""
    ## Infrastructure is the Missing Yield Engine
    
    Every onchain action begins before a transaction hits a mempool. Wallets and apps read state, fetch balances, query logs, 
    estimate gas and call methods thousands of times per second across the ecosystem. Those remote procedure calls (RPCs) are 
    the unseen API of Web3, and they're essential for everything from wallets to rollups. Historically, the bills for those 
    requests live offchain as invoices to node providers and are paid in fiat.
    
    The scale is enormous. Ankr, a Web3-native infrastructure provider, processes over **1 trillion monthly RPC requests** 
    across 90 blockchains, showing that the data plane of crypto is where the vast majority of user interactions actually happen. 
    Yet almost none of that spend circulates back onchain to deepen liquidity or reward the apps generating the load.
    
    That gap suggests a simple idea: **if gas fees can enrich networks onchain, why can't RPC spend do the same?** 
    Turning infrastructure costs into chain-owned liquidity would convert a perpetual expense into a compounding asset — 
    an always-on, usage-indexed source of yield.
    """)
    
    st.markdown("""
    ## Turning Calls into Capital with RPCfi
    
    RPCfi is a new primitive offered by Neura, an EVM-compatible layer-1 blockchain purpose-built for stablecoins, DeFi and 
    real-time digital finance. It captures RPC spend at the infrastructure layer and cycles it into onchain liquidity and rewards. 
    Where traditional setups let value leak to offchain bills, RPCfi reroutes a share of that demand toward liquidity provisioning 
    and points or rewards programs to create an engine that scales with usage.
    
    > *"If gas fees reward computation and staking rewards security, RPCfi rewards the very pulse of Web3 — data access"*  
    > — Neura CEO Arsalan Evini
    
    This approach arrives alongside a broader push to align base-layer economics with real activity. RPCfi sits within a broader 
    toolkit that pairs deterministic, high-throughput infrastructure with demand-based revenue streams, so builders, validators and 
    users compound together as usage grows.
    """)
    
    st.markdown("""
    ## The Solution in Practice
    
    Here's how RPCfi works in practice:
    
    1. **A decentralized application (DApp) spends $10,000 per month** on Ankr's Premium RPC services on Tron.
    2. **Under the new RPCfi model, 50% of that spend ($5,000)** is automatically captured and redirected onchain.
    3. **The first step** is bridging the USD value to the Neura blockchain.
    4. **Then $5,000 is used to purchase equal portions of TRX and ANKR** — $2,500 allocated to each side of the pair.
    5. **The resulting assets are deposited** into a liquidity pool via Zotto, Neura's flagship veDEX/AMM.
    6. **Rewards generated** by that liquidity position (emissions and RPCfi points) flow directly back to the originating DApp.
    7. **The DApp can then choose** how to use those rewards: distribute to holders, reward stakers, or reinvest.
    
    This model goes live at the mainnet launch, integrated natively with Ankr's existing infrastructure business.
    
    Teams can map their existing RPC line items to a recurring liquidity strategy, treating infrastructure as a budget line that earns. 
    Chain-owned LPs reduce reliance on mercenary capital, stabilize markets with tighter spreads and unlock new incentives for sticky users. 
    As traffic scales, the liquidity base grows with it, forming an organic moat rooted in usage rather than emissions.
    """)
    
    st.markdown("""
    ## Why This Finally Works
    
    Historically, node providers behaved like Web2 SaaS with offchain billing, fiat payments and no onchain recapture.
    
    Ankr aims to change that. As a Web3-native RPC provider, it can uniquely redirect RPC value flows back into blockchain economics.
    
    This partnership between Neura and Ankr closes the loop. RPC costs that once drained out of the ecosystem are now recycled as 
    onchain liquidity and rewards, reinforcing the very networks that generate them.
    """)
    
    st.markdown("""
    ## New Era for Real-Time Finance
    
    Neura was designed to power the next generation of real-time global finance — fast, cheap and stable. But with RPCfi, it also 
    introduces something deeper: a built-in, infrastructure-native yield mechanism that ties every transaction, every query and every 
    DApp interaction directly into the value of the network.
    
    DeFi's next chapter favors yield that scales with real activity and revenue. By converting the internet backstage of crypto — 
    every balance lookup, log query and contract call — into onchain liquidity, Neura's RPCfi offers a path to resilient rewards 
    and durable network effects. It turns a hidden cost center into the backbone of a healthier DeFi economy.
    """)
    
    # Growth Assumptions Section (modular, selectable)
    st.markdown("---")
    st.subheader("Growth Assumptions in This Simulation")

    growth_scenarios = {
        "Conservative": {
            "description": "Flat-to-low growth with conservative projections",
            "initial": 1.0,
            "future": 1.8,
            "approach": "Focus on current revenue with limited future growth"
        },
        "Moderate": {
            "description": "Moderate growth with steady expansion",
            "initial": 1.5,
            "future": 2.0,
            "approach": "Steady growth based on historical trends and adoption"
        },
        "Optimistic": {
            "description": "Aggressive growth with high adoption",
            "initial": 2.0,
            "future": 3.5,
            "approach": "High growth scenario with strong market adoption"
        }
    }

    selected_scenario = st.selectbox(
        "Select Growth Scenario:",
        options=list(growth_scenarios.keys()),
        index=1
    )

    scenario = growth_scenarios[selected_scenario]
    st.session_state["rpcfi_growth_initial_multiplier"] = scenario["initial"]
    st.session_state["rpcfi_growth_future_multiplier"] = scenario["future"]
    st.session_state["rpcfi_selected_growth_scenario"] = selected_scenario

    st.markdown(f"""
    **Selected Scenario: {selected_scenario}**

    {scenario['description']}

    **Revenue Model:**
    - **Base Revenue**: Uses last historical month as baseline, scaled by initial multiplier
    - **Initial Growth**: {scenario['initial']}x immediately applied
    - **Future Growth**: Linear ramp to {scenario['future']}x over simulation period
    - **Growth Approach**: {scenario['approach']}

    **Revenue Split:**
    - **50%** goes to infrastructure costs
    - **25%** used for TRX buybacks
    - **25%** used for ANKR buybacks

    **APY Scenarios:**
    - **Worst Case**: 20% APY
    - **Base Case**: 30% APY  
    - **Best Case**: 40% APY

    **Key Mechanics:**
    - All buybacks are converted to LP tokens (TRX/ANKR pairs)
    - LP grows from new buyback deposits (no auto-compounding)
    - Yields are paid out (not reinvested)
    - Foundation LP remains constant at $100,000
    """)

def show_overview_page(simulator: RPCfiSimulator):
    """Display the overview page"""
    st.header("Simulation Overview")
    
    # Apply selected growth settings from About tab
    if "rpcfi_growth_initial_multiplier" in st.session_state:
        simulator.growth_multiplier = st.session_state["rpcfi_growth_initial_multiplier"]
    if "rpcfi_growth_future_multiplier" in st.session_state:
        simulator.expected_future_growth_multiplier = st.session_state["rpcfi_growth_future_multiplier"]

    # APY Scenario Selection
    st.subheader("APY Scenario")
    apy_scenario = st.selectbox(
        "Select APY Scenario:",
        options=list(simulator.apy_scenarios.keys()),
        format_func=lambda x: f"{x.title()} Case ({simulator.apy_scenarios[x]}% APY)"
    )
    
    # Show selected scenario info
    selected_apy = simulator.apy_scenarios[apy_scenario]
    st.info(f"Selected: **{apy_scenario.title()} Case** with **{selected_apy}% APY**")
    
    # Run simulation
    if st.button("Run Simulation", type="primary"):
        with st.spinner("Running simulation..."):
            simulation_results = simulator.run_simulation(apy_scenario)
        
        # Display summary metrics
        st.subheader("Simulation Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_revenue = simulation_results['RPC_Revenue_USD'].sum()
            st.metric("Total RPC Revenue", f"${total_revenue:,.0f}")
        
        with col2:
            total_buybacks = (simulation_results['TRX_Buyback_USD'] + simulation_results['ANKR_Buyback_USD']).sum()
            st.metric("Total Buybacks", f"${total_buybacks:,.0f}")
        
        with col3:
            final_lp_tvl = simulation_results['Total_LP_TVL_USD'].iloc[-1]
            st.metric("Final LP TVL", f"${final_lp_tvl:,.0f}")
        
        with col4:
            total_dev_yield = simulation_results['Cumulative_Dev_Yield_USD'].iloc[-1]
            st.metric("Total Dev Yield", f"${total_dev_yield:,.0f}")
        
        # Growth assumptions
        st.subheader("Growth Assumptions")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Initial Growth Multiplier", f"{simulator.growth_multiplier}x")
        
        with col2:
            st.metric("Future Growth Multiplier", f"{simulator.expected_future_growth_multiplier}x")
        
        # Token prices
        st.subheader("Token Prices")
        price_cols = st.columns(len(simulator.token_prices))
        for i, (token, price) in enumerate(simulator.token_prices.items()):
            with price_cols[i]:
                st.metric(f"{token} Price", f"${price:.3f}")
        
        # Historical data summary
        if simulator.historical_data:
            st.subheader("Historical Revenue Data")
            historical_df = pd.DataFrame(list(simulator.historical_data.items()), columns=['Month', 'Revenue (USD)'])
            st.dataframe(historical_df, use_container_width=True)

def show_buyback_page(simulator: RPCfiSimulator):
    """Display the buyback and LP flows page"""
    st.header("Buyback & LP Flows")
    
    if simulator.simulation_data is None:
        st.warning("Please run the simulation first from the Overview page.")
        return
    
    # Weekly buyback amounts
    st.subheader("Weekly Buyback Amounts")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(f'{simulator.native_token} Buybacks', f'{simulator.governance_token} Buybacks'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['TRX_Buyback_USD'],
            mode='lines+markers',
            name=f'{simulator.native_token} Buybacks',
            line=dict(color='#e74c3c')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['ANKR_Buyback_USD'],
            mode='lines+markers',
            name=f'{simulator.governance_token} Buybacks',
            line=dict(color='#3498db')
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="Weekly Buyback Amounts (USD)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # LP TVL Growth
    st.subheader("LP TVL Growth")
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=simulator.simulation_data['Date'],
        y=simulator.simulation_data['Cumulative_RPCfi_LP_USD'],
        mode='lines+markers',
        name='RPCfi LP',
        line=dict(color='#3498db', width=3)
    ))
    
    # Add foundation LP (constant)
    foundation_lp_value = sum(simulator.initial_lp.values())
    fig2.add_trace(go.Scatter(
        x=simulator.simulation_data['Date'],
        y=[foundation_lp_value] * len(simulator.simulation_data),
        mode='lines',
        name='Foundation LP',
        line=dict(color='#e74c3c', width=2, dash='dash')
    ))
    
    fig2.add_trace(go.Scatter(
        x=simulator.simulation_data['Date'],
        y=simulator.simulation_data['Total_LP_TVL_USD'],
        mode='lines+markers',
        name='Total LP TVL',
        line=dict(color='#2c3e50', width=3)
    ))
    
    fig2.update_layout(
        title="Cumulative LP TVL Growth",
        xaxis_title="Date",
        yaxis_title="LP Value (USD)",
        height=500
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Weekly LP minted table
    st.subheader("Weekly LP Details")
    
    display_data = simulator.simulation_data[['Date', 'Weekly_LP_Value_USD', 'Cumulative_RPCfi_LP_USD', 'Total_LP_TVL_USD']].copy()
    display_data['Date'] = display_data['Date'].dt.strftime('%Y-%m-%d')
    display_data = display_data.round(2)
    
    st.dataframe(
        display_data,
        column_config={
            "Date": "Date",
            "Weekly_LP_Value_USD": st.column_config.NumberColumn("Weekly LP Minted (USD)", format="$%.2f"),
            "Cumulative_RPCfi_LP_USD": st.column_config.NumberColumn("Cumulative RPCfi LP (USD)", format="$%.2f"),
            "Total_LP_TVL_USD": st.column_config.NumberColumn("Total LP TVL (USD)", format="$%.2f")
        },
        use_container_width=True
    )

def show_yield_page(simulator: RPCfiSimulator):
    """Display the yield and revenue page"""
    st.header("Yield & Revenue")
    
    if simulator.simulation_data is None:
        st.warning("Please run the simulation first from the Overview page.")
        return
    
    # Yield comparison
    st.subheader("Weekly Yield Comparison")
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Weekly Yields', 'Cumulative Yields'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['Dev_Weekly_Yield_USD'],
            mode='lines+markers',
            name='Developer Weekly Yield',
            line=dict(color='#3498db')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['Foundation_Weekly_Yield_USD'],
            mode='lines+markers',
            name='Foundation Weekly Yield',
            line=dict(color='#e74c3c')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['Cumulative_Dev_Yield_USD'],
            mode='lines+markers',
            name='Cumulative Developer Yield',
            line=dict(color='#3498db', width=3),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=simulator.simulation_data['Date'],
            y=simulator.simulation_data['Cumulative_Foundation_Yield_USD'],
            mode='lines+markers',
            name='Cumulative Foundation Yield',
            line=dict(color='#e74c3c', width=3),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=700,
        showlegend=True,
        title_text="Yield Distribution Over Time"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Yield summary metrics
    st.subheader("Yield Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        final_dev_yield = simulator.simulation_data['Cumulative_Dev_Yield_USD'].iloc[-1]
        st.metric("Total Developer Yield", f"${final_dev_yield:,.0f}")
    
    with col2:
        final_foundation_yield = simulator.simulation_data['Cumulative_Foundation_Yield_USD'].iloc[-1]
        st.metric("Total Foundation Yield", f"${final_foundation_yield:,.0f}")
    
    with col3:
        avg_weekly_dev_yield = simulator.simulation_data['Dev_Weekly_Yield_USD'].mean()
        st.metric("Avg Weekly Dev Yield", f"${avg_weekly_dev_yield:,.0f}")
    
    with col4:
        avg_weekly_foundation_yield = simulator.simulation_data['Foundation_Weekly_Yield_USD'].mean()
        st.metric("Avg Weekly Foundation Yield", f"${avg_weekly_foundation_yield:,.0f}")
    
    # Detailed yield table
    st.subheader("Detailed Yield Data")
    
    yield_data = simulator.simulation_data[['Date', 'Dev_Weekly_Yield_USD', 'Foundation_Weekly_Yield_USD', 
                                          'Cumulative_Dev_Yield_USD', 'Cumulative_Foundation_Yield_USD']].copy()
    yield_data['Date'] = yield_data['Date'].dt.strftime('%Y-%m-%d')
    yield_data = yield_data.round(2)
    
    st.dataframe(
        yield_data,
        column_config={
            "Date": "Date",
            "Dev_Weekly_Yield_USD": st.column_config.NumberColumn("Dev Weekly Yield (USD)", format="$%.2f"),
            "Foundation_Weekly_Yield_USD": st.column_config.NumberColumn("Foundation Weekly Yield (USD)", format="$%.2f"),
            "Cumulative_Dev_Yield_USD": st.column_config.NumberColumn("Cumulative Dev Yield (USD)", format="$%.2f"),
            "Cumulative_Foundation_Yield_USD": st.column_config.NumberColumn("Cumulative Foundation Yield (USD)", format="$%.2f")
        },
        use_container_width=True
    )

if __name__ == "__main__":
    main()
