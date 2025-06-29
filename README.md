# 🎧 Telegram Annotation Bot for HamNava Dataset

This repository contains the implementation of a Telegram bot used for **crowd-sourced multi-label instrument classification** in **Iranian classical music**, as part of the creation of the [HamNava dataset](#hamnava-dataset-summary).

The bot automates the process of distributing audio excerpts to volunteers, collecting their confidence-based judgments for each instrument, and managing user profiles based on self-declared and tested proficiency levels.

---

## 📁 Repository Structure

```
├── main.py                       # Main Telegram bot logic
├── dataset/
   ├── samples/                  # Main audio excerpts to be annotated
    └── truth/                    # Audio clips for ear-training test
└── dataframe/
    ├── annotation.xlsx           # Full annotation logs with confidence scores and timestamps
    ├── samples.xlsx              # Metadata for all audio samples (track names, paths, difficulty)
    └── user.xlsx                 # Stores user info and hearing test performance
```
---

## 🔍 File Descriptions
 - dataset/samples/: Contains all 5-second audio clips that will be presented to users for annotation.

 - truth/: Contains audio files used to evaluate users' music hearing ability (instrument recognition). Users are tested on these clips before being assigned to the easy/hard group.

 - samples.xlsx: Lists all audio clips in the dataset with metadata and difficulty level.

 - user.xlsx: Tracks each user's self-evaluation, hearing test responses, and annotation contributions.

 - dataframe/annotation.xlsx: Raw annotation records including user ID, sample ID, selected confidence scores for each instrument, and timestamps.

## 🧠 Annotation Logic
 - Each user listens to a 5-second mono .mp3 audio clip (22.05 kHz).

 - Labels 9 musical elements:

   - tar, setar, santur, oud, kamancheh, ney, tonbak, daf, vocal

 - Confidence levels:

   - 0 → Not heard

   - 1, 2, 3 → Increasing certainty (mapped to 0.5, 0.75, and 1.0)

 - Annotators are split into two groups:

   - Easy: Clearer clips with instrument contrast

   - Hard: Densely layered or similar technique instruments

   - Users are assigned based on their performance on a music hearing test using clips in truth/.


# 📊 HamNava Dataset Summary
 - The HamNava dataset was created using this bot and contains:

📁 Dataset Contents
 - audio/: 6,000 audio excerpts (.mp3, 5 seconds, 22.05 kHz mono)

 - annotations/:

   -  train.csv, validation.csv, test.csv – soft labels

   - train_bin.csv, validation_bin.csv, test_bin.csv – binarized at threshold 0.5

   - Each .csv contains:
        - sample_id
        - Labels for tar, setar, santur, oud, kamancheh, ney, tonbak, daf, vocal
        - difficulty: binary (0 = easy, 1 = hard)

- For more information refere to the [webpage](https://navaalab.github.io/resources/dataset/hamnava.html).


## 📄 License
 - This repository is provided under the MIT License.
 - The HamNava dataset is available for non-commercial research use only.
