"""
Script to join all_grants_combined.csv with NSF-Terminated-Awards.csv
and add a 'terminated' column to indicate if a grant has been terminated.
"""

import pandas as pd
from pathlib import Path


def join_terminated_grants(base_dir: str):
    """
    Join grants data with terminated awards and add terminated flag.
    
    Args:
        base_dir: Directory containing the CSV files
    """
    base_path = Path(base_dir)
    
    # Read the combined grants file
    print("Reading all_grants_combined.csv...")
    grants_file = base_path / "all_grants_combined.csv"
    grants_df = pd.read_csv(grants_file)
    print(f"  - Loaded {len(grants_df):,} grants")
    print()
    
    # Read the terminated awards file
    print("Reading NSF-Terminated-Awards.csv...")
    terminated_file = base_path / "NSF-Terminated-Awards.csv"
    
    try:
        terminated_df = pd.read_csv(terminated_file, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            terminated_df = pd.read_csv(terminated_file, encoding='latin-1')
        except UnicodeDecodeError:
            terminated_df = pd.read_csv(terminated_file, encoding='cp1252')
    
    # Extract the Award ID column (first column)
    # Clean up the Award ID by removing any whitespace
    terminated_ids = set(terminated_df['Award ID'].astype(str).str.strip())
    
    print(f"  - Found {len(terminated_ids):,} terminated awards")
    print()
    
    # Add the terminated column
    print("Adding 'terminated' column to grants data...")
    # Convert awd_id to string and strip whitespace for comparison
    grants_df['terminated'] = grants_df['awd_id'].astype(str).str.strip().isin(terminated_ids)
    
    # Count how many grants are marked as terminated
    num_terminated = grants_df['terminated'].sum()
    print(f"  - Marked {num_terminated:,} grants as terminated")
    print(f"  - {len(grants_df) - num_terminated:,} grants are active")
    print()
    
    # Save the result
    output_file = base_path / "all_grants_with_termination.csv"
    print(f"Saving joined data to {output_file}...")
    grants_df.to_csv(output_file, index=False)
    
    # Show breakdown by year
    print("Terminated Grants by Year:")
    print("-" * 40)
    year_summary = grants_df.groupby('year')['terminated'].agg(['sum', 'count'])
    year_summary.columns = ['Terminated', 'Total']
    year_summary['Percentage'] = (year_summary['Terminated'] / year_summary['Total'] * 100).round(2)
    print(year_summary)
    print()
    
    print("=" * 80)


def main():
    """Main function."""
    base_dir = Path(__file__).parent
    join_terminated_grants(str(base_dir))


if __name__ == "__main__":
    main()

