import os
import numpy as np
import tensorflow as tf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import pandas as pd

def load_feature_files(directory):
    data = []
    file_info = []
    file_count = 0
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_count += 1
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            features = df.values
            for row_num, row in enumerate(features):
                data.append(row)
                file_info.append((filename, row_num))
    return np.array(data), file_info, file_count

# Update the function call for training data
feature_dir = "peak_detection/features_output"
X_train, train_file_info, train_file_count = load_feature_files(feature_dir)
print(f"Number of training files: {train_file_count}")

def find_optimal_clusters(X, max_clusters=10):
    silhouette_scores = []
    for n_clusters in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X)
        silhouette_avg = silhouette_score(X, cluster_labels)
        silhouette_scores.append(silhouette_avg)
    
    optimal_clusters = silhouette_scores.index(max(silhouette_scores)) + 2
    return optimal_clusters

# Find optimal number of clusters
optimal_clusters = find_optimal_clusters(X_train)
print(f"Optimal number of clusters: {optimal_clusters}")

class AnomalyDetector:
    def __init__(self, n_clusters):
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters)
    
    def fit(self, X):
        X_scaled = self.scaler.fit_transform(X)
        self.kmeans.fit(X_scaled)
    
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        distances = self.kmeans.transform(X_scaled)
        return np.min(distances, axis=1)

detector = AnomalyDetector(n_clusters=optimal_clusters)
detector.fit(X_train)

class TFAnomalyDetector(tf.Module):
    def __init__(self, kmeans, scaler):
        self.n_clusters = kmeans.n_clusters
        self.centroids = tf.Variable(kmeans.cluster_centers_, dtype=tf.float32)
        self.scaler_mean = tf.Variable(scaler.mean_, dtype=tf.float32)
        self.scaler_scale = tf.Variable(scaler.scale_, dtype=tf.float32)
    
    # @tf.function(input_signature=[tf.TensorSpec(shape=[1, 84], dtype=tf.float32)])
    @tf.function(input_signature=[tf.TensorSpec(shape=[1, 42], dtype=tf.float32)])
    def __call__(self, x):
        x_scaled = (x - self.scaler_mean) / self.scaler_scale
        distances = tf.reduce_sum(tf.square(tf.expand_dims(x_scaled, axis=1) - self.centroids), axis=2)
        return tf.reduce_min(distances, axis=1)

tf_detector = TFAnomalyDetector(detector.kmeans, detector.scaler)

converter = tf.lite.TFLiteConverter.from_keras_model(tf_detector)
tflite_model = converter.convert()

with open('peak_detection/hopping_anomaly_detector.tflite', 'wb') as f:
    f.write(tflite_model)

interpreter = tf.lite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()

def get_tflite_predictions(interpreter, X):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    results = []
    for sample in X:
        # interpreter.set_tensor(input_details[0]['index'], sample.reshape(1, 84).astype(np.float32))
        interpreter.set_tensor(input_details[0]['index'], sample.reshape(1, 42).astype(np.float32))
        interpreter.invoke()
        results.append(interpreter.get_tensor(output_details[0]['index'])[0])
    return np.array(results)

tflite_train_results = get_tflite_predictions(interpreter, X_train)
threshold = np.percentile(tflite_train_results, 70)
print(f"\nAnomaly threshold (based on TFLite model): {threshold}")

test_dir = "peak_detection/test_data"
X_test, test_file_info, test_file_count = load_feature_files(test_dir)
print(f"Number of test files: {test_file_count}")

tflite_test_results = get_tflite_predictions(interpreter, X_test)

def should_be_anomaly(filename):
    return "Stand on one leg" in filename or "Criss Cross" in filename

print("\nTFLite Model Anomaly Detection:")
correct_predictions = 0
total_predictions = 0

for (filename, row_num), result, anomaly_score in zip(test_file_info, tflite_test_results > threshold, tflite_test_results):
    expected_anomaly = should_be_anomaly(filename)
    is_correct = (result == expected_anomaly)
    correct_predictions += int(is_correct)
    total_predictions += 1
    print(f"File: {filename}, Row: {row_num}, Is Anomaly: {result}, Anomaly Score: {anomaly_score}, Correct: {is_correct}")

# Summary
anomaly_counts = {}
file_accuracies = {}

for (filename, _), result in zip(test_file_info, tflite_test_results > threshold):
    if filename not in anomaly_counts:
        anomaly_counts[filename] = {"total": 0, "anomalies": 0, "correct": 0}
    anomaly_counts[filename]["total"] += 1
    if result:
        anomaly_counts[filename]["anomalies"] += 1
    if result == should_be_anomaly(filename):
        anomaly_counts[filename]["correct"] += 1

print("\nSummary:")
overall_correct = 0
overall_total = 0

for filename, counts in anomaly_counts.items():
    print(f"File: {filename}")
    print(f"  Total rows: {counts['total']}")
    print(f"  Anomalies detected: {counts['anomalies']}")
    print(f"  Correct predictions: {counts['correct']}")
    accuracy = (counts['correct'] / counts['total']) * 100
    print(f"  Accuracy: {accuracy:.2f}%")
    print()
    
    overall_correct += counts['correct']
    overall_total += counts['total']

overall_accuracy = (overall_correct / overall_total) * 100
print(f"\nOverall Accuracy: {overall_accuracy:.2f}%")
print(f"Total Correct Predictions: {overall_correct}")
print(f"Total Predictions: {overall_total}")