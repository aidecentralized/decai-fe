import numpy as np
import os
import json
from tqdm import tqdm

def convert_npz_to_json(npz_path: str, output_dir: str, data_flag: str):
    """
    Converts the BloodMNIST .npz dataset to JSON files for train and test splits.

    Parameters:
    - npz_path (str): Path to the .npz file.
    - output_dir (str): Directory where JSON files will be saved.
    - data_flag (str): Dataset flag (e.g., 'bloodmnist') for naming output files.
    """
    # Validate that the output directory exists to avoid creating new folders
    if not os.path.exists(output_dir):
        raise ValueError(f"The directory '{output_dir}' does not exist. Please provide a valid path.")

    # Load the .npz file
    data = np.load(npz_path)

    # Map dataset splits to their respective keys
    splits = {
        'train': ('train_images', 'train_labels'),
        'test': ('test_images', 'test_labels')
    }

    def process_and_save(split, images_key, labels_key):
        print(f"Processing {split} data...")
        images = data[images_key]
        labels = data[labels_key]

        # Flatten and format the data for JSON
        samples = []
        for idx in tqdm(range(len(images)), desc=f"Processing {split} samples"):
            img_array = images[idx].flatten().tolist()
            label = int(labels[idx])  # Convert to int
            samples.append({
                'image': img_array,
                'label': label
            })

        # Save to JSON
        output_file = os.path.join(output_dir, f"{data_flag}_{split}.json")
        with open(output_file, 'w') as f:
            json.dump(samples, f)
        print(f"Saved {split} data to {output_file}")

    # Process and save each split (train and test only)
    for split, (images_key, labels_key) in splits.items():
        process_and_save(split, images_key, labels_key)

    print("Conversion completed successfully!")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert MedMNIST .npz dataset to JSON.")
    parser.add_argument('--npz_path', type=str, required=True, help="Path to the .npz file.")
    parser.add_argument(
        '--output_dir',
        type=str,
        default='/Users/ayanshsingh/on-device-training-classification-model/on_device_training/web/web-bundler/public/data',
        help="Absolute path to the directory where JSON files will be saved."
    )
    parser.add_argument('--data_flag', type=str, default='bloodmnist', help="Dataset flag for naming output files.")
    
    args = parser.parse_args()
    convert_npz_to_json(args.npz_path, args.output_dir, args.data_flag)
