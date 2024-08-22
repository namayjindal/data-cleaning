import os
import pandas as pd
import numpy as np
import glob

exercises_to_columns = {
    "Step Down from Height (dominant)": [3, 4],
    "Step Down from Height (non-dominant)": [3, 4],
    "Step over an obstacle (dominant)": [3, 4],
    "Step over an obstacle (non-dominant)": [3, 4],
    "Jump symmetrically": [3, 4],
    "Hit Balloon Up": [1, 2],
    "Stand on one leg (dominant)": [3, 4],
    "Stand on one leg (non-dominant)": [3, 4],
    "Hop forward on one leg (dominant)": [3, 4],
    "Hop forward on one leg (non-dominant)": [3, 4],
    "Jumping Jack without Clap": [3, 4],
    "Dribbling in Fig - 8": [1, 2, 3, 4, 5],
    "Dribbling in Fig - O": [1, 2, 3, 4, 5],
    "Jumping Jack with Clap": [1, 2, 3, 4],
    "Criss Cross with Clap": [1, 2, 3, 4],
    "Criss Cross without Clap": [3, 4],
    "Criss Cross with leg forward": [3, 4],
    "Skipping": [1, 2, 3, 4],
    "Large Ball Bounce and Catch": [1, 2, 5],
    "Forward Backward Spread Legs and Back": [3, 4],
    "Alternate feet forward backward": [3, 4],
    "Jump asymmetrically": [3, 4],
    "Hop 9 metres (dominant)": [3, 4],
    "Hop 9 metres (non-dominant)": [3, 4],
}

def reorder_columns(df, file_name):
    prefixes = ['right_hand', 'left_hand', 'right_leg', 'left_leg', 'ball']
    reordered_columns = []
    exercise_name = os.path.splitext(os.path.basename(file_name))[0].split('-')[0]
    
    if exercise_name in exercises_to_columns:
        column_indices = exercises_to_columns[exercise_name]
        for prefix, index in zip(prefixes, column_indices):
            reordered_columns.extend([col for col in df.columns if col.startswith(prefixes[index-1])])
    else:
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

def extract_date_from_filename(file_name):
    timestamp_part = file_name.split('-')[-1]  # Extracts the last part of the file name
    date_str = timestamp_part[:8]  # Extract the date part (YYYYMMDD)
    return date_str

def process_file(file_path, output_base_dir):
    print(f"Processing file: {file_path}")
    
    # Check if file is empty or contains only headers
    if os.stat(file_path).st_size == 0:
        print(f"Skipping empty file: {file_path}")
        return
    
    df = pd.read_csv(file_path)
    
    # Skip files with only headers
    if df.empty or len(df.columns) == 0:
        print(f"Skipping file with only headers: {file_path}")
        return
    
    # Reorder and filter columns
    df = reorder_columns(df, file_path)
    
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
    
    # Extract date from the file name and create a corresponding directory
    date_str = extract_date_from_filename(os.path.basename(file_path))
    output_dir = os.path.join(output_base_dir, date_str)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save the cleaned data
    output_path = os.path.join(output_dir, os.path.basename(file_path))
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to: {output_path}")

def main():
    input_dir = 'data'
    output_base_dir = 'cleaned_data'
    
    if not os.path.exists(output_base_dir):
        os.makedirs(output_base_dir)
    
    for file_path in glob.glob(os.path.join(input_dir, '*.csv')):
        process_file(file_path, output_base_dir)

if __name__ == "__main__":
    main()