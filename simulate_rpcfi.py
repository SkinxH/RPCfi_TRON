#!/usr/bin/env python3
"""
RPCfi Data Generator - Helper script to generate synthetic RPC revenue data
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import argparse
import os

def generate_synthetic_revenue_data(
    start_month: str = "2025-04",
    end_month: str = "2025-09",
    base_revenue: float = 15000,
    growth_rate: float = 0.0,
    volatility: float = 0.05
) -> dict:
    """
    Generate synthetic RPC revenue data with flat revenue (no growth assumptions)
    
    Args:
        start_month: Start month in YYYY-MM format
        end_month: End month in YYYY-MM format
        base_revenue: Base monthly revenue in USD
        growth_rate: Monthly growth rate (0.0 = no growth)
        volatility: Random volatility factor (0.05 = 5% random variation)
    
    Returns:
        Dictionary with month-revenue pairs
    """
    # Parse dates
    start_date = datetime.strptime(start_month, "%Y-%m")
    end_date = datetime.strptime(end_month, "%Y-%m")
    
    # Generate months
    current_date = start_date
    revenue_data = {}
    month_count = 0
    
    while current_date <= end_date:
        # Calculate base revenue with growth
        monthly_revenue = base_revenue * ((1 + growth_rate) ** month_count)
        
        # Add random volatility
        random_factor = np.random.normal(1.0, volatility)
        monthly_revenue *= random_factor
        
        # Ensure positive revenue
        monthly_revenue = max(monthly_revenue, base_revenue * 0.5)
        
        # Round to nearest thousand
        monthly_revenue = round(monthly_revenue, -3)
        
        # Store data
        month_key = current_date.strftime("%Y-%m")
        revenue_data[month_key] = monthly_revenue
        
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
        
        month_count += 1
    
    return revenue_data

def generate_multiple_scenarios() -> dict:
    """Generate multiple revenue scenarios for comparison"""
    scenarios = {
        "conservative": generate_synthetic_revenue_data(
            base_revenue=12000,
            growth_rate=0.0,
            volatility=0.02
        ),
        "moderate": generate_synthetic_revenue_data(
            base_revenue=15000,
            growth_rate=0.0,
            volatility=0.05
        ),
        "aggressive": generate_synthetic_revenue_data(
            base_revenue=20000,
            growth_rate=0.0,
            volatility=0.08
        ),
        "volatile": generate_synthetic_revenue_data(
            base_revenue=15000,
            growth_rate=0.0,
            volatility=0.15
        )
    }
    return scenarios

def save_to_csv(revenue_data: dict, filename: str):
    """Save revenue data to CSV file"""
    df = pd.DataFrame(list(revenue_data.items()), columns=['Month', 'RPC_Revenue_USD'])
    df.to_csv(filename, index=False)
    print(f"Revenue data saved to {filename}")

def save_to_json(revenue_data: dict, filename: str):
    """Save revenue data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(revenue_data, f, indent=2)
    print(f"Revenue data saved to {filename}")

def create_sample_configs():
    """Create sample configuration files for different chains"""
    configs = {
        "tron": {
            "chain_name": "Tron",
            "native_token": "TRX",
            "rpcfi_partner": "Ankr",
            "governance_token": "ANKR",
            "base_currency": "USD",
            "token_prices": {
                "TRX": 0.12,
                "ANKR": 0.025,
                "ANKR": 0.025
            },
            "initial_lp": {
                "Tron Foundation": 50000,
                "Ankr Foundation": 50000
            },
            "growth_multiplier": 1.4,
            "expected_future_growth_multiplier": 2.0,
            "start_date": "2025-01-15",
            "historical_window": {
                "start": "2025-04-01",
                "end": "2025-09-30"
            },
            "apy_settings": {
                "foundation_base_apy": 10.0,
                "developer_base_apy": 12.0,
                "veboost_factor": 1.8
            }
        },
        "ethereum": {
            "chain_name": "Ethereum",
            "native_token": "ETH",
            "rpcfi_partner": "Ankr",
            "governance_token": "ANKR",
            "base_currency": "USD",
            "token_prices": {
                "ETH": 2500.0,
                "ANKR": 0.025,
                "ANKR": 0.025
            },
            "initial_lp": {
                "Ethereum Foundation": 50000,
                "Ankr Foundation": 50000
            },
            "growth_multiplier": 1.2,
            "expected_future_growth_multiplier": 1.8,
            "start_date": "2025-01-15",
            "historical_window": {
                "start": "2025-04-01",
                "end": "2025-09-30"
            },
            "apy_settings": {
                "foundation_base_apy": 8.0,
                "developer_base_apy": 10.0,
                "veboost_factor": 1.6
            }
        },
        "polygon": {
            "chain_name": "Polygon",
            "native_token": "MATIC",
            "rpcfi_partner": "Ankr",
            "governance_token": "ANKR",
            "base_currency": "USD",
            "token_prices": {
                "MATIC": 0.85,
                "ANKR": 0.025,
                "ANKR": 0.025
            },
            "initial_lp": {
                "Polygon Foundation": 50000,
                "Ankr Foundation": 50000
            },
            "growth_multiplier": 1.5,
            "expected_future_growth_multiplier": 2.2,
            "start_date": "2025-01-15",
            "historical_window": {
                "start": "2025-04-01",
                "end": "2025-09-30"
            },
            "apy_settings": {
                "foundation_base_apy": 12.0,
                "developer_base_apy": 15.0,
                "veboost_factor": 2.0
            }
        }
    }
    
    for chain, config in configs.items():
        filename = f"config_{chain}.json"
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Created {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic RPCfi revenue data")
    parser.add_argument("--scenario", choices=["conservative", "moderate", "aggressive", "volatile", "all"], 
                       default="moderate", help="Revenue scenario to generate")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="both", 
                       help="Output format")
    parser.add_argument("--output", default="revenue_data", help="Output filename prefix")
    parser.add_argument("--create-configs", action="store_true", 
                       help="Create sample configuration files")
    
    args = parser.parse_args()
    
    if args.create_configs:
        print("Creating sample configuration files...")
        create_sample_configs()
        return
    
    if args.scenario == "all":
        scenarios = generate_multiple_scenarios()
        for scenario_name, revenue_data in scenarios.items():
            print(f"\nGenerating {scenario_name} scenario:")
            print(f"Total 6-month revenue: ${sum(revenue_data.values()):,.0f}")
            
            if args.format in ["csv", "both"]:
                save_to_csv(revenue_data, f"{args.output}_{scenario_name}.csv")
            if args.format in ["json", "both"]:
                save_to_json(revenue_data, f"{args.output}_{scenario_name}.json")
    else:
        # Generate single scenario
        if args.scenario == "conservative":
            revenue_data = generate_synthetic_revenue_data(base_revenue=12000, growth_rate=0.0, volatility=0.02)
        elif args.scenario == "moderate":
            revenue_data = generate_synthetic_revenue_data(base_revenue=15000, growth_rate=0.0, volatility=0.05)
        elif args.scenario == "aggressive":
            revenue_data = generate_synthetic_revenue_data(base_revenue=20000, growth_rate=0.0, volatility=0.08)
        elif args.scenario == "volatile":
            revenue_data = generate_synthetic_revenue_data(base_revenue=15000, growth_rate=0.0, volatility=0.15)
        
        print(f"Generated {args.scenario} scenario:")
        print(f"Total 6-month revenue: ${sum(revenue_data.values()):,.0f}")
        print("\nMonthly breakdown:")
        for month, revenue in revenue_data.items():
            print(f"  {month}: ${revenue:,.0f}")
        
        if args.format in ["csv", "both"]:
            save_to_csv(revenue_data, f"{args.output}_{args.scenario}.csv")
        if args.format in ["json", "both"]:
            save_to_json(revenue_data, f"{args.output}_{args.scenario}.json")

if __name__ == "__main__":
    main()
