#!/usr/bin/env python3
"""
Multi-DAO Collector
Unified script to collect data from multiple DAOs (Arbitrum, Optimism, Uniswap, Aave)
"""

import os
import sys
import argparse
from typing import List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def collect_dao_data(dao_name: str, data_type: str = "all"):
    """
    Collect data for a specific DAO
    
    Args:
        dao_name: Name of the DAO (arbitrum, optimism, uniswap, aave)
        data_type: Type of data to collect (snapshot, onchain, all)
    """
    dao_name = dao_name.lower()
    
    if dao_name not in ["arbitrum", "optimism", "uniswap", "aave"]:
        print(f"Error: Unknown DAO '{dao_name}'")
        print("Supported DAOs: arbitrum, optimism, uniswap, aave")
        return False
    
    print(f"\n{'='*60}")
    print(f"Collecting data for {dao_name.upper()} DAO")
    print(f"Data type: {data_type}")
    print(f"{'='*60}\n")
    
    success = True
    
    # Collect Snapshot data
    if data_type in ["snapshot", "all"]:
        print(f"\n--- Collecting Snapshot data for {dao_name.upper()} ---")
        try:
            if dao_name == "arbitrum":
                from snapshot_collector import main as snapshot_main
            elif dao_name == "optimism":
                from optimism_collector import main as snapshot_main
            elif dao_name == "uniswap":
                from uniswap_collector import main as snapshot_main
            elif dao_name == "aave":
                from aave_collector import main as snapshot_main
            
            snapshot_main()
            print(f"✓ Snapshot data collection complete for {dao_name.upper()}")
        except Exception as e:
            print(f"✗ Error collecting Snapshot data for {dao_name}: {e}")
            success = False
    
    # Collect on-chain data
    if data_type in ["onchain", "all"]:
        print(f"\n--- Collecting on-chain data for {dao_name.upper()} ---")
        try:
            if dao_name == "arbitrum":
                from onchain_collector import main as onchain_main
            elif dao_name == "optimism":
                from optimism_onchain_collector import main as onchain_main
            elif dao_name == "uniswap":
                from uniswap_onchain_collector import main as onchain_main
            elif dao_name == "aave":
                from aave_onchain_collector import main as onchain_main
            
            onchain_main()
            print(f"✓ On-chain data collection complete for {dao_name.upper()}")
        except Exception as e:
            print(f"✗ Error collecting on-chain data for {dao_name}: {e}")
            success = False
    
    return success

def collect_all_daos(data_type: str = "all"):
    """
    Collect data for all supported DAOs
    """
    daos = ["arbitrum", "optimism", "uniswap", "aave"]
    
    print("\n" + "="*60)
    print("Multi-DAO Data Collection")
    print(f"Collecting {data_type} data for all DAOs")
    print("="*60)
    
    results = {}
    for dao in daos:
        results[dao] = collect_dao_data(dao, data_type)
    
    # Print summary
    print("\n" + "="*60)
    print("Collection Summary")
    print("="*60)
    for dao, success in results.items():
        status = "✓ Success" if success else "✗ Failed"
        print(f"{dao.upper():15} {status}")
    print("="*60)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-DAO data collector for Arbitrum, Optimism, Uniswap, and Aave"
    )
    parser.add_argument(
        "--dao",
        choices=["arbitrum", "optimism", "uniswap", "aave", "all"],
        default="all",
        help="DAO to collect data from (default: all)"
    )
    parser.add_argument(
        "--type",
        choices=["snapshot", "onchain", "all"],
        default="all",
        help="Type of data to collect (default: all)"
    )
    
    args = parser.parse_args()
    
    if args.dao == "all":
        collect_all_daos(args.type)
    else:
        collect_dao_data(args.dao, args.type)

if __name__ == "__main__":
    main()
