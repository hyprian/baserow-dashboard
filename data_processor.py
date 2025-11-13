# data_processor.py

import yaml
import pandas as pd
from clients.baserow_client import BaserowClient

def process_dataframe(df, dc_config, luc_config):
    """Helper function to calculate date ranges from a dataframe."""
    min_date_str, max_date_str, last_updated_str = "N/A", "N/A", None
    
    # Process main date column
    if dc_config and dc_config['name'] in df.columns:
        # --- ROBUST CLEANING LOGIC ---
        # 1. Get the raw series, drop nulls, and ensure it's treated as a string
        raw_series = df[dc_config['name']].dropna().astype(str)
        # 2. Clean the strings: remove leading/trailing whitespace (like \n) and any quotes
        cleaned_series = raw_series.str.strip().str.strip('"')
        # 3. Now convert the CLEANED series to datetime
        date_series = pd.to_datetime(cleaned_series, dayfirst=dc_config.get('dayfirst', False), errors='coerce')
        # --- END OF FIX ---
        valid_dates = date_series.dropna()
        if not valid_dates.empty:
            min_date_str = valid_dates.min().strftime('%d-%b-%Y')
            max_date_str = valid_dates.max().strftime('%d-%b-%Y')
            
    # Process last updated column
    if luc_config and luc_config['name'] in df.columns:
        raw_series_luc = df[luc_config['name']].dropna().astype(str)
        cleaned_series_luc = raw_series_luc.str.strip().str.strip('"')
        update_series = pd.to_datetime(cleaned_series_luc, dayfirst=luc_config.get('dayfirst', False), errors='coerce')
        valid_updates = update_series.dropna()
        if not valid_updates.empty:
            last_updated_str = valid_updates.max().strftime('%d-%b-%Y %H:%M')
            
    return min_date_str, max_date_str, last_updated_str

def get_all_date_ranges():
    with open('settings.yaml', 'r') as f:
        config = yaml.safe_load(f)

    client = BaserowClient(api_token=config['baserow']['api_token'], base_url=config['baserow']['base_url'])
    all_group_data = []

    for group in config.get('groups', []):
        group_results = {"group_name": group['name'], "tables": []}
        
        for table_name, table_info in group.get('tables', {}).items():
            table_type = table_info.get('type', 'single')
            table_id = table_info['table_id']

            # --- NEW LOGIC BRANCH ---
            if table_type == 'panels':
                print(f"Processing PANELS for '{table_name}'")
                df = client.get_table_as_dataframe(table_id)
                if df.empty: continue
                
                panel_cfg = table_info['panel_config']
                filter_cols = panel_cfg['filter_columns']
                
                for panel in panel_cfg['panels']:
                    card_title = panel['card_title']
                    filter_vals = panel['filter_values']
                    
                    # Dynamically build the filter mask
                    mask = (df[filter_cols[0]] == filter_vals[0]) & (df[filter_cols[1]] == filter_vals[1])
                    filtered_df = df[mask]
                    
                    min_d, max_d, last_upd = process_dataframe(filtered_df, table_info.get('date_column'), table_info.get('last_updated_column'))
                    
                    group_results["tables"].append({
                        "table_name": card_title,
                        "min_date": min_d, "max_date": max_d,
                        "last_updated": last_upd, "status_message": "OK"
                    })

            # --- ORIGINAL LOGIC FOR SINGLE TABLES ---
            else: # type == 'single'
                print(f"Processing SINGLE table '{table_name}'")
                df = client.get_table_as_dataframe(table_id)
                
                min_d, max_d, last_upd = process_dataframe(df, table_info.get('date_column'), table_info.get('last_updated_column'))
                
                group_results["tables"].append({
                    "table_name": table_name,
                    "min_date": min_d, "max_date": max_d,
                    "last_updated": last_upd, "status_message": "OK" if not df.empty else "No data found"
                })
        
        all_group_data.append(group_results)
        
    return all_group_data