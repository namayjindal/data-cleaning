import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_data_from_csv(file_path):
    # Load the CSV data
    df = pd.read_csv(file_path)

    # Remove unwanted columns
    columns_to_keep = [
        'left_leg_timestamp', 'left_leg_accel_x', 'left_leg_accel_y', 'left_leg_accel_z',
        'left_leg_gyro_x', 'left_leg_gyro_y', 'left_leg_gyro_z'
    ]
    df = df[columns_to_keep]

    # Plotting the data
    plt.figure(figsize=(10, 6))

    plt.plot(df['left_leg_timestamp'], df['left_leg_accel_x'], label='Accel X')
    plt.plot(df['left_leg_timestamp'], df['left_leg_accel_y'], label='Accel Y')
    plt.plot(df['left_leg_timestamp'], df['left_leg_accel_z'], label='Accel Z')
    plt.plot(df['left_leg_timestamp'], df['left_leg_gyro_x'], label='Gyro X')
    plt.plot(df['left_leg_timestamp'], df['left_leg_gyro_y'], label='Gyro Y')
    plt.plot(df['left_leg_timestamp'], df['left_leg_gyro_z'], label='Gyro Z')

    # Adding labels and legend
    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensor Values')
    plt.title(f'Sensor Data from {os.path.basename(file_path)}')
    plt.legend()

    # Save the plots
    plt.savefig(f'{os.path.basename(file_path)}.png')

def plot_all_files_in_directory(directory_path):
    # Iterate over all files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            plot_data_from_csv(file_path)

# Replace 'your_directory' with the actual directory name
directory_path = ''
plot_all_files_in_directory(directory_path)

