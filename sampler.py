import pandas as pd
import soundfile as sf
import os

# Load the Excel file
excel_path = 'songs.xlsx'  # Update with your actual path if different
df = pd.read_excel(excel_path)


df[['آواز', 'تار', 'سه تار', 'تنبک', 'سنتور', 'کمانچه', 'نی']] = df[['آواز', 'تار', 'سه تار', 'تنبک', 'سنتور', 'کمانچه', 'نی']].fillna(0)

print(df)
# Output directory for the clips
output_dir = 'clips'
os.makedirs(output_dir, exist_ok=True)

# Function to create 5-second clips
def create_clips(row):
    # Construct the path
    file_path = f"music-dataset/{row['هنرمند']}/{row['آلبوم']}/{row['قطعه']}.mp3"
    
    try:
        audio, sr = sf.read(file_path, dtype='float32')
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return
    
    song_id = str(row['id']).zfill(3)
    level = row['سطح']
    
    duration = len(audio) / sr  # duration of the song in seconds
    clip_duration = 5  # 5 seconds
    
    num_clips = int(duration // clip_duration)

    clip_info_list = []
    
    for i in range(num_clips):
        start_time = i * clip_duration
        end_time = start_time + clip_duration
        clip = audio[int(start_time * sr):int(end_time * sr)]
        
        clip_filename = f"{song_id}-{i+1:03d}-{level}.mp3"
        clip_path = os.path.join(output_dir, clip_filename)
        
        try:
            sf.write(clip_path, clip, sr)
            print(f"Exported {clip_path}")

            clip_info = {
                'sample_id': clip_filename,
                'level': level,
                'num_annotation': 0,
                'singer': row['آواز'],
                'tar': row['تار'],
                'ney': row['نی'],
                'setar': row['سه تار'],
                'santour': row['سنتور'],
                'kamancheh': row['کمانچه'],
                'tonbak': row['تنبک']
            }
            clip_info_list.append(clip_info)

            
        except Exception as e:
            print(f"Error exporting clip {clip_path}: {e}")

    return clip_info_list

# List to collect all clip information
all_clips_info = []

#df.apply(create_clips, axis=1)

# Process each song in the DataFrame
for _, row in df.iterrows():
    clips_info = create_clips(row)
    all_clips_info.extend(clips_info)

# Create a DataFrame with the clip information
clips_df = pd.DataFrame(all_clips_info)

# Save the new DataFrame to an Excel file
output_excel_path = 'samples.xlsx'
clips_df.to_excel(output_excel_path, index=False)


print("All clips have been created.")
