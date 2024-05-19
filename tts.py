import os
import hashlib
import random  # Add this import
from TTS.api import TTS
import torch
from transformers import pipeline
from config import CACHE_DIR, GENERIC_MALE_DIR, GENERIC_FEMALE_DIR, MAPPINGS_FILE_PATH
from mappings import sample_mappings, save_mappings

# Initialize TTS models
device = "cuda" if torch.cuda.is_available() else "cpu"
print("Initializing TTS models...")
coqui_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
print("TTS models initialized.")

# Initialize emotion detection pipeline
emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

# Function to normalize NPC names
def normalize_npc_name(npc_name):
    normalized_name = npc_name.replace(" ", "_").replace("'", "")
    print(f"Raw NPC name: {npc_name}, Normalized NPC name: {normalized_name}")
    return normalized_name

# Function to infer emotion from text
def infer_emotion(text):
    result = emotion_classifier(text)
    print(f"Emotion classification result: {result}")  # Debugging statement
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list) and len(result[0]) > 0:
        return result[0][0]['label']
    return 'neutral'

# Function to get a unique file path for caching audio based on the NPC name and text
def get_cache_path(npc_name, text):
    hash_object = hashlib.md5(text.encode())
    file_name = f"{hash_object.hexdigest()}.wav"
    npc_cache_dir = os.path.join(CACHE_DIR, npc_name)
    os.makedirs(npc_cache_dir, exist_ok=True)
    return os.path.join(npc_cache_dir, file_name)

# Function to get or assign a speaker ID, voice sample path, and accent based on the NPC and voice gender
async def get_speaker_info(npc_name, voice_gender):
    if npc_name in sample_mappings:
        info = sample_mappings[npc_name]
        return info.get("speaker_id", ""), info.get("voice_sample", None), info.get("accent", None)
    
    sample_dir = GENERIC_MALE_DIR if voice_gender.lower() == "male" else GENERIC_FEMALE_DIR

    # Select a random sample from the generic directory
    voice_samples = os.listdir(sample_dir)
    selected_sample = os.path.join(sample_dir, random.choice(voice_samples))
    
    sample_mappings[npc_name] = {"voice_sample": selected_sample}
    await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
    return "", selected_sample, None

# Function to update the mappings with voice sample paths and accents
async def update_voice_sample(npc_name, voice_sample_path, accent=None):
    if npc_name in sample_mappings:
        sample_mappings[npc_name]["voice_sample"] = voice_sample_path
        if accent:
            sample_mappings[npc_name]["accent"] = accent
    else:
        sample_mappings[npc_name] = {"voice_sample": voice_sample_path, "accent": accent}
    await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
