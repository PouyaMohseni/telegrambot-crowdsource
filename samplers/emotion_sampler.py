import pandas as pd
import numpy as np
import soundfile as sf
import os
import random

# Load the dataset
df = pd.read_excel('emotion_samples.xlsx')

# Define the output directory
output_dir = 'output_samples'

# Create the output directory if it does not exist
os.makedirs(output_dir, exist_ok=True)

# Function to process each audio file
def process_audio(row):
    try:
        # Load the audio file
        data, samplerate = sf.read(row['mp3_path'])
        
        # Calculate the total duration of the audio in seconds
        total_duration_seconds = len(data) / samplerate
        
        # Check if the audio is less than 1:30 (90 seconds)
        if total_duration_seconds < 90:
            print(f"Audio file {row['mp3_path']} is too short (less than 1:30). Skipping.")
            return
        
        # Calculate the duration of the second and third fourths of the audio in samples
        total_samples = len(data)
        second_and_third_fourth_start = total_samples // 4
        second_and_third_fourth_end = 3 * (total_samples // 4)
        segment_samples = int(samplerate * 20)  # 20 seconds of audio
        
        # Ensure the segment can be extracted
        if (second_and_third_fourth_end - second_and_third_fourth_start) < segment_samples:
            print(f"Audio file {row['mp3_path']} is too short to extract 20 seconds from the second and third fourths.")
            return
        
        # Randomly select a start point within the second and third fourth of the audio
        start_sample = random.randint(second_and_third_fourth_start, second_and_third_fourth_end - segment_samples)
        end_sample = start_sample + segment_samples

        # Extract the segment
        audio_segment = data[start_sample:end_sample]

        # Format the new file name
        new_file_name = f"{str(row['id']).zfill(3)}-000-{row['level']}.mp3"
        
        # Define the full path for the new file
        output_path = os.path.join(output_dir, new_file_name)
        
        # Save the segment
        sf.write(output_path, audio_segment, samplerate)
        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {row['mp3_path']}: {e}")

# Apply the function to each row in the dataframe
df.apply(process_audio, axis=1)
