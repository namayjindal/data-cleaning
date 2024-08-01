import os
import pandas as pd
import numpy as np
import glob

def reorder_columns(df):
    prefixes = ['right_hand', 'left_hand', 'right_leg', 'left_leg', 'ball']
    reordered_columns = []
    for prefix in prefixes:
        reordered_columns.extend([col for col in df.columns if col.startswith(prefix)])
    return df[reordered_columns]

def is_row_valid(row):
    return all((-1e10 < x < 1e10) if isinstance(x, (int, float)) else True for x in row)

def remove_abnormal_rows(df):
    valid_rows = df.apply(is_row_valid, axis=1)
    if not valid_rows.all():
        print(f"Removed {(~valid_rows).sum()} rows with abnormal values.")
    return df[valid_rows].reset_index(drop=True)

def find_valid_start_index(df, timestamp_cols):
    start_indices = []
    for col in timestamp_cols:
        start_index = df.index[df[col] < 1].min()
        if pd.notna(start_index):
            start_indices.append(start_index)
    
    if not start_indices:
        return None
    return max(start_indices)

def process_file(file_path, output_dir):
    print(f"Processing file: {file_path}")
    df = pd.read_csv(file_path)
    
    # Reorder columns
    df = reorder_columns(df)
    
    # Remove rows with abnormal values
    df = remove_abnormal_rows(df)
    
    # Find all timestamp columns
    timestamp_cols = [col for col in df.columns if 'timestamp' in col]
    
    # Find the valid start index based on all timestamp columns
    start_index = find_valid_start_index(df, timestamp_cols)
    
    if start_index is None:
        print(f"Warning: No valid timestamps less than 1 second found in {file_path}")
        return
    
    # Cut out rows before the valid start index
    df = df.loc[start_index:].reset_index(drop=True)
    
    # Check for and remove duplicate index values
    index_cols = [col for col in df.columns if 'index' in col]
    for col in index_cols:
        duplicates = df[col].duplicated()
        if duplicates.sum() > 0:
            print(f"Found {duplicates.sum()} duplicate index values in column {col}. Removing them.")
            df = df[~duplicates]
    
    # Check for timestamp differences
    for col in timestamp_cols:
        time_diff = df[col].diff()
        large_gaps = (time_diff > 0.1).sum()
        if large_gaps > 20:
            print(f"Alert: {large_gaps} instances of timestamp differences exceeding 100ms in column {col}")
    
    # Save the cleaned data
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to: {output_path}")

def main():
    input_dir = 'data'
    output_dir = 'cleaned_data'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for file_path in glob.glob(os.path.join(input_dir, '*.csv')):
        process_file(file_path, output_dir)

if __name__ == "__main__":
    main()