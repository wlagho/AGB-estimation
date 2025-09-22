# # scripts/data_exploration.py
# from datasets import load_dataset
# import numpy as np

# def explore_agbd_dataset():
#     """Explore the AGBD dataset structure and contents"""
#     print("Loading AGBD dataset from HuggingFace...")
    
#     try:
#         # Try without trust_remote_code parameter
#         dataset = load_dataset('prs-eth/AGBD', streaming=True)
#         print("Dataset loaded successfully!")
#     except Exception as e:
#         print(f"Error loading with streaming: {e}")
#         try:
#             # Try without streaming
#             dataset = load_dataset('prs-eth/AGBD')
#             print("Dataset loaded without streaming!")
#         except Exception as e2:
#             print(f"Error loading without streaming: {e2}")
#             return None
    
#     train_dataset = dataset["train"]
    
#     # Rest of exploration code...
#     sample_count = 0
#     for sample in train_dataset:
#         if sample_count >= 3:
#             break
            
#         print(f"\nSample {sample_count + 1}:")
#         print(f"Keys available: {list(sample.keys())}")
#         print(f"Input shape: {sample['input'].shape}")
#         print(f"Label (AGB): {sample['label']}")
        
#         sample_count += 1
    
#     return dataset

# if __name__ == "__main__":
#     explore_agbd_dataset()

from datasets import load_dataset
import numpy as np

def explore_cached_agbd():
    """Explore already downloaded part of AGBD dataset."""
    print("Loading local AGBD dataset from Hugging Face cache...")

    try:
        # Load from local cache only, no streaming
        dataset = load_dataset('prs-eth/AGBD', download_mode='reuse_cache_if_exists')
        print("Dataset loaded from cache successfully!")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None

    train_dataset = dataset["train"]

    # Explore first 3 available samples
    print("\nExploring a few samples:")
    for idx in range(3):
        try:
            sample = train_dataset[idx]
            print(f"\nSample {idx + 1}:")
            print(f"Keys: {list(sample.keys())}")
            print(f"Input shape: {sample['input'].shape}")
            print(f"Label (AGB): {sample['label']}")
        except Exception as e:
            print(f"Error accessing sample {idx}: {e}")
            break

    return dataset

if __name__ == "__main__":
    explore_cached_agbd()
