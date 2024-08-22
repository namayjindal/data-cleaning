import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_data_from_csv(file_path):
    # Load the CSV data
    df = pd.read_csv(file_path)

    # Remove unwanted columns
    columns_to_keep = [
        'right_leg_timestamp', 'right_leg_accel_x', 'right_leg_accel_y', 'right_leg_accel_z',
        'right_leg_gyro_x', 'right_leg_gyro_y', 'right_leg_gyro_z', 'left_leg_accel_x', 'left_leg_accel_y', 'left_leg_accel_z',
        'left_leg_gyro_x', 'left_leg_gyro_y', 'left_leg_gyro_z'
    ]
    df = df[columns_to_keep]

    # Plotting the data
    plt.figure(figsize=(10, 6))

    plt.plot(df['right_leg_timestamp'], df['right_leg_accel_x'], label='RL Accel X')
    plt.plot(df['right_leg_timestamp'], df['right_leg_accel_y'], label='RL Accel Y')
    plt.plot(df['right_leg_timestamp'], df['right_leg_accel_z'], label='RL Accel Z')
    plt.plot(df['right_leg_timestamp'], df['right_leg_gyro_x'], label='RL Gyro X')
    plt.plot(df['right_leg_timestamp'], df['right_leg_gyro_y'], label='RL Gyro Y')
    plt.plot(df['right_leg_timestamp'], df['right_leg_gyro_z'], label='RL Gyro Z')
    plt.plot(df['right_leg_timestamp'], df['left_leg_accel_x'], label='LL Accel X')
    plt.plot(df['right_leg_timestamp'], df['left_leg_accel_y'], label='LL Accel Y')
    plt.plot(df['right_leg_timestamp'], df['left_leg_accel_z'], label='LL Accel Z')
    plt.plot(df['right_leg_timestamp'], df['left_leg_gyro_x'], label='LL Gyro X')
    plt.plot(df['right_leg_timestamp'], df['left_leg_gyro_y'], label='LL Gyro Y')
    plt.plot(df['right_leg_timestamp'], df['left_leg_gyro_z'], label='LL Gyro Z')

    # Adding labels and legend
    plt.xlabel('Time (seconds)')
    plt.ylabel('Sensor Values')
    plt.title(f'Sensor Data from {os.path.basename(file_path)}')

    # Moving the legend outside of the plot
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Adjust layout to make room for the legend
    plt.tight_layout(rect=[0, 0, 0.8, 1])

    # Save the plots
    plt.savefig(f'{os.path.basename(file_path)}.png')

def plot_all_files_in_directory(directory_path):
    # Iterate over all files in the given directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(directory_path, filename)
            plot_data_from_csv(file_path)

# Replace 'your_directory' with the actual directory name
directory_path = 'plots/hopping'
plot_all_files_in_directory(directory_path)
