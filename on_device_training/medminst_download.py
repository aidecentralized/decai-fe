import numpy as np

# Path to the .npz file
file_path = '/Users/ayanshsingh/.medmnist/bloodmnist.npz'

# Load the .npz file
data = np.load(file_path)

# List all available keys in the file
print(f"Keys in the file: {data.keys()}")

# Access specific subsets of the dataset
train_images = data['train_images']
train_labels = data['train_labels']
val_images = data['val_images']
val_labels = data['val_labels']
test_images = data['test_images']

# Print shapes to verify
print(f"Train images shape: {train_images.shape}")
print(f"Train labels shape: {train_labels.shape}")
print(f"Validation images shape: {val_images.shape}")
print(f"Validation labels shape: {val_labels.shape}")
print(f"Test images shape: {test_images.shape}")
