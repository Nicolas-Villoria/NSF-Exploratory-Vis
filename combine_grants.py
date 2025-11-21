#!/usr/bin/env python3
"""
Script to concatenate all yearly grant CSV files and add a year column.
"""

import pandas as pd
from pathlib import Path


def combine_yearly_grants(base_dir: str, output_file: str):
    """
    Combine all yearly grant CSV files into a single CSV with a year column.
    
    Args:
        base_dir: Directory containing the yearly CSV files
        output_file: Path to the output combined CSV file
    """
    base_path = Path(base_dir)
    years = ['2020', '2021', '2022', '2023', '2024', '2025']
    
    all_dataframes = []
    
    print("=" * 80)
    print("Combining NSF Grants CSV Files")
    print("=" * 80)
    print()
    
    for year in years:
        csv_file = base_path / f"grants_{year}.csv"
        
        if not csv_file.exists():
            print(f"Warning: {csv_file} not found, skipping...")
            continue
        
        print(f"Reading {csv_file.name}...")
        df = pd.read_csv(csv_file)
        
        # Add year column
        df['year'] = int(year)
        
        print(f"  - Loaded {len(df):,} grants from {year}")
        all_dataframes.append(df)
    
    print()
    print("Concatenating all dataframes...")
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Reorder columns to put 'year' as the first column
    cols = combined_df.columns.tolist()
    cols.remove('year')
    cols = ['year'] + cols
    combined_df = combined_df[cols]
    
    print(f"Total grants: {len(combined_df):,}")
    print()
    
    print(f"Writing combined data to {output_file}...")
    combined_df.to_csv(output_file, index=False)
    
    print(f"✓ Successfully created {output_file}")
    print()
    
    # Print summary statistics
    print("Summary by Year:")
    print("-" * 40)
    year_counts = combined_df['year'].value_counts().sort_index()
    for year, count in year_counts.items():
        print(f"  {year}: {count:,} grants")
    
    print()
    print("=" * 80)


def main():
    """Main function."""
    base_dir = Path(__file__).parent
    output_file = base_dir / "all_grants_combined.csv"
    
    combine_yearly_grants(str(base_dir), str(output_file))


if __name__ == "__main__":
    main()

