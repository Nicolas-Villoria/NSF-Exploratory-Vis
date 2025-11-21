#!/usr/bin/env python3
"""
Script to process NSF grant JSON files and create CSV documents for each year.
This script reads all JSON files from year directories (2021-2025) and extracts
relevant grant information into CSV format.
"""

import json
import csv
import os
from pathlib import Path
from typing import Dict, List, Any


def extract_grant_data(json_file_path: str) -> Dict[str, Any]:
    """
    Extract relevant fields from a grant JSON file.
    
    Args:
        json_file_path: Path to the JSON file
        
    Returns:
        Dictionary containing extracted grant data
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract basic grant information
        grant_info = {
            'awd_id': data.get('awd_id', ''),
            'agcy_id': data.get('agcy_id', ''),
            'tran_type': data.get('tran_type', ''),
            'awd_istr_txt': data.get('awd_istr_txt', ''),
            'awd_titl_txt': data.get('awd_titl_txt', ''),
            'cfda_num': data.get('cfda_num', ''),
            'org_code': data.get('org_code', ''),
            'po_phone': data.get('po_phone', ''),
            'po_email': data.get('po_email', ''),
            'po_sign_block_name': data.get('po_sign_block_name', ''),
            'awd_eff_date': data.get('awd_eff_date', ''),
            'awd_exp_date': data.get('awd_exp_date', ''),
            'tot_intn_awd_amt': data.get('tot_intn_awd_amt', ''),
            'awd_amount': data.get('awd_amount', ''),
            'awd_min_amd_letter_date': data.get('awd_min_amd_letter_date', ''),
            'awd_max_amd_letter_date': data.get('awd_max_amd_letter_date', ''),
            'awd_arra_amount': data.get('awd_arra_amount', ''),
            'dir_abbr': data.get('dir_abbr', ''),
            'org_dir_long_name': data.get('org_dir_long_name', ''),
            'div_abbr': data.get('div_abbr', ''),
            'org_div_long_name': data.get('org_div_long_name', ''),
            'awd_agcy_code': data.get('awd_agcy_code', ''),
            'fund_agcy_code': data.get('fund_agcy_code', ''),
        }
        
        # Extract principal investigator information
        pi_list = data.get('pi', [])
        if pi_list and len(pi_list) > 0:
            pi = pi_list[0]  # Primary PI
            grant_info['pi_role'] = pi.get('pi_role', '')
            grant_info['pi_first_name'] = pi.get('pi_first_name', '')
            grant_info['pi_last_name'] = pi.get('pi_last_name', '')
            grant_info['pi_mid_init'] = pi.get('pi_mid_init', '')
            grant_info['pi_full_name'] = pi.get('pi_full_name', '')
            grant_info['pi_email_addr'] = pi.get('pi_email_addr', '')
            grant_info['nsf_id'] = pi.get('nsf_id', '')
        else:
            grant_info['pi_role'] = ''
            grant_info['pi_first_name'] = ''
            grant_info['pi_last_name'] = ''
            grant_info['pi_mid_init'] = ''
            grant_info['pi_full_name'] = ''
            grant_info['pi_email_addr'] = ''
            grant_info['nsf_id'] = ''
        
        # Count co-PIs
        grant_info['num_co_pis'] = len([p for p in pi_list if p.get('pi_role') == 'Co-Principal Investigator'])
        
        # Extract institution information
        inst = data.get('inst', {})
        grant_info['inst_name'] = inst.get('inst_name', '')
        grant_info['inst_street_address'] = inst.get('inst_street_address', '')
        grant_info['inst_city_name'] = inst.get('inst_city_name', '')
        grant_info['inst_state_code'] = inst.get('inst_state_code', '')
        grant_info['inst_state_name'] = inst.get('inst_state_name', '')
        grant_info['inst_zip_code'] = inst.get('inst_zip_code', '')
        grant_info['inst_country_name'] = inst.get('inst_country_name', '')
        grant_info['cong_dist_code'] = inst.get('cong_dist_code', '')
        grant_info['st_cong_dist_code'] = inst.get('st_cong_dist_code', '')
        grant_info['org_lgl_bus_name'] = inst.get('org_lgl_bus_name', '')
        grant_info['org_uei_num'] = inst.get('org_uei_num', '')
        
        # Extract performance institution information
        perf_inst = data.get('perf_inst', {})
        grant_info['perf_inst_name'] = perf_inst.get('perf_inst_name', '')
        grant_info['perf_city_name'] = perf_inst.get('perf_city_name', '')
        grant_info['perf_st_code'] = perf_inst.get('perf_st_code', '')
        grant_info['perf_st_name'] = perf_inst.get('perf_st_name', '')
        grant_info['perf_zip_code'] = perf_inst.get('perf_zip_code', '')
        grant_info['perf_cong_dist'] = perf_inst.get('perf_cong_dist', '')
        grant_info['perf_st_cong_dist'] = perf_inst.get('perf_st_cong_dist', '')
        grant_info['perf_ctry_name'] = perf_inst.get('perf_ctry_name', '')
        
        # Extract program reference information
        pgm_ref = data.get('pgm_ref', [])
        if pgm_ref and len(pgm_ref) > 0:
            grant_info['pgm_ref_code'] = pgm_ref[0].get('pgm_ref_code', '')
            grant_info['pgm_ref_txt'] = pgm_ref[0].get('pgm_ref_txt', '')
        else:
            grant_info['pgm_ref_code'] = ''
            grant_info['pgm_ref_txt'] = ''
        
        # Extract obligation fiscal year information
        oblg_fy = data.get('oblg_fy', [])
        if oblg_fy and len(oblg_fy) > 0:
            grant_info['fund_oblg_fiscal_yr'] = oblg_fy[0].get('fund_oblg_fiscal_yr', '')
            grant_info['fund_oblg_amt'] = oblg_fy[0].get('fund_oblg_amt', '')
        else:
            grant_info['fund_oblg_fiscal_yr'] = ''
            grant_info['fund_oblg_amt'] = ''
        
        return grant_info
        
    except Exception as e:
        print(f"Error processing {json_file_path}: {e}")
        return None


def process_year_directory(year_dir: str, output_csv: str) -> int:
    """
    Process all JSON files in a year directory and create a CSV file.
    
    Args:
        year_dir: Path to the year directory containing JSON files
        output_csv: Path to the output CSV file
        
    Returns:
        Number of grants processed
    """
    year_path = Path(year_dir)
    
    if not year_path.exists():
        print(f"Directory {year_dir} does not exist!")
        return 0
    
    # Get all JSON files in the directory
    json_files = list(year_path.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in {year_dir}")
        return 0
    
    print(f"Processing {len(json_files)} grants from {year_path.name}...")
    
    # Process all JSON files
    all_grants = []
    for json_file in json_files:
        grant_data = extract_grant_data(str(json_file))
        if grant_data:
            all_grants.append(grant_data)
    
    # Write to CSV
    if all_grants:
        fieldnames = list(all_grants[0].keys())
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_grants)
        
        print(f"Created {output_csv} with {len(all_grants)} grants")
        return len(all_grants)
    
    return 0


def main():
    """Main function to process all year directories."""
    # Get the base directory (where this script is located)
    base_dir = Path(__file__).parent
    
    years = ['2020', '2021', '2022', '2023', '2024', '2025']
    
    total_grants = 0
    
    print("=" * 80)
    print("NSF Grants CSV Generation")
    print("=" * 80)
    print()
    
    for year in years:
        year_dir = base_dir / year
        output_csv = base_dir / f"grants_{year}.csv"
        
        count = process_year_directory(str(year_dir), str(output_csv))
        total_grants += count
        print()
    
    print("=" * 80)
    print(f"Total grants processed: {total_grants}")
    print("=" * 80)


if __name__ == "__main__":
    main()

