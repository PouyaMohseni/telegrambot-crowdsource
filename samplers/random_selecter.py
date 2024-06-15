import os
import random
import pandas as pd

def select_random_mp3(path):
    second_level_folders_paths = []
    selected_mp3_paths = []

    # Iterate through the top-level directories
    for top_level_item in os.listdir(path):
        top_level_path = os.path.join(path, top_level_item)
        if os.path.isdir(top_level_path):
            # Iterate through the second-level directories
            for second_level_item in os.listdir(top_level_path):
                second_level_path = os.path.join(top_level_path, second_level_item)
                if os.path.isdir(second_level_path):
                    second_level_folders_paths.append(second_level_path)

    # Select a random mp3 from each second-level folder
    for folder in second_level_folders_paths:
        mp3_files = [f for f in os.listdir(folder) if f.endswith('.mp3')]
        if mp3_files:
            selected_mp3 = random.choice(mp3_files)
            selected_mp3_path = os.path.join(folder, selected_mp3)
            selected_mp3_paths.append(selected_mp3_path)
    
    return selected_mp3_paths

# Example usage
path_to_parent_folder = 'music-dataset'
selected_mp3_paths = select_random_mp3(path_to_parent_folder)

# Save to a CSV file
df = pd.DataFrame(selected_mp3_paths, columns=['mp3_path'])
df.to_excel('selected_mp3_paths.xlsx', index=False)

print("Paths to selected MP3 files have been saved to 'selected_mp3_paths.csv'.")

