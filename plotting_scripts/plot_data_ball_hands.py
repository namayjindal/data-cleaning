import matplotlib.pyplot as plt
import pandas as pd
import os

def plot_data_from_csv(file_path):
    # Load the CSV data
    df = pd.read_csv(file_path)

    # Remove unwanted columns
    columns_to_keep = [
        'right_hand_timestamp', 'right_hand_accel_x', 'right_hand_accel_y', 'right_hand_accel_z',
        'right_hand_gyro_x', 'right_hand_gyro_y', 'right_hand_gyro_z', 'ball_accel_x', 'ball_accel_y', 'ball_accel_z', 'ball_gyro_x', 'ball_gyro_y', 'ball_gyro_z'
    ]
    df = df[columns_to_keep]

    # Plotting the data
    plt.figure(figsize=(10, 6))

    plt.plot(df['right_hand_timestamp'], df['right_hand_accel_x'], label='Accel X')
    plt.plot(df['right_hand_timestamp'], df['right_hand_accel_y'], label='Accel Y')
    plt.plot(df['right_hand_timestamp'], df['right_hand_accel_z'], label='Accel Z')
    plt.plot(df['right_hand_timestamp'], df['right_hand_gyro_x'], label='Gyro X')
    plt.plot(df['right_hand_timestamp'], df['right_hand_gyro_y'], label='Gyro Y')
    plt.plot(df['right_hand_timestamp'], df['right_hand_gyro_z'], label='Gyro Z')
    plt.plot(df['right_hand_timestamp'], df['ball_accel_x'], label='Ball Accel X')
    plt.plot(df['right_hand_timestamp'], df['ball_accel_y'], label='Ball Accel Y')
    plt.plot(df['right_hand_timestamp'], df['ball_accel_z'], label='Ball Accel Z')
    plt.plot(df['right_hand_timestamp'], df['ball_gyro_x'], label='Ball Gyro X')
    plt.plot(df['right_hand_timestamp'], df['ball_gyro_y'], label='Ball Gyro Y')
    plt.plot(df['right_hand_timestamp'], df['ball_gyro_z'], label='Ball Gyro Z')

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
directory_path = 'plots/ball_bounce_and_catch'
plot_all_files_in_directory(directory_path)
