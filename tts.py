import os
import hashlib
import random  # Add this import
from TTS.api import TTS
import torch
from transformers import pipeline
from config import CACHE_DIR, GENERIC_MALE_DIR, GENERIC_FEMALE_DIR, MAPPINGS_FILE_PATH
from mappings import sample_mappings, save_mappings
from logger import log_message
# Initialize TTS models
device = "cuda" if torch.cuda.is_available() else "cpu"

log_message(f"Initializing TTS models on {device}...")
try:
    coqui_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    log_message("TTS models initialized.")
except Exception as e:
    log_message(f"Error initializing TTS model: {e}")
    coqui_tts = None

emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

def normalize_npc_name(npc_name):
    normalized_name = npc_name.replace(" ", "_").replace("'", "")
    print(f"Raw NPC name: {npc_name}, Normalized NPC name: {normalized_name}")
    return normalized_name

def infer_emotion(text):
    result = emotion_classifier(text)
    print(f"Emotion classification result: {result}")  # Debugging statement
    if result and isinstance(result, list) and len(result) > 0:
        top_result = result[0]
        if isinstance(top_result, dict) and 'label' in top_result:
            return top_result['label']
    return 'neutral'


GENERIC_MALE_SAMPLES = os.listdir(GENERIC_MALE_DIR)
GENERIC_FEMALE_SAMPLES = os.listdir(GENERIC_FEMALE_DIR)

def get_cache_path(npc_name, text):
    hash_object = hashlib.md5(text.encode())
    file_name = f"{hash_object.hexdigest()}.wav"
    npc_cache_dir = os.path.join(CACHE_DIR, npc_name)
    if not os.path.exists(npc_cache_dir):
        os.makedirs(npc_cache_dir, exist_ok=True)
    return os.path.join(npc_cache_dir, file_name)

speaker_info_cache = {}

async def get_speaker_info(npc_name, voice_gender):
    if npc_name in speaker_info_cache:
        return speaker_info_cache[npc_name]
    
    if npc_name in sample_mappings:
        info = sample_mappings[npc_name]
        speaker_id = info.get("speaker_id", "")
        voice_sample = info.get("voice_sample", None)
        accent = info.get("accent", None)
        speaker_info_cache[npc_name] = (speaker_id, voice_sample, accent)
        return speaker_id, voice_sample, accent

    sample_dir = GENERIC_MALE_DIR if voice_gender.lower() == "male" else GENERIC_FEMALE_DIR
    voice_samples = GENERIC_MALE_SAMPLES if voice_gender.lower() == "male" else GENERIC_FEMALE_SAMPLES

    selected_sample = os.path.join(sample_dir, random.choice(voice_samples))
    sample_mappings[npc_name] = {"voice_sample": selected_sample}
    await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
    speaker_info_cache[npc_name] = ("", selected_sample, None)
    return "", selected_sample, None

async def update_voice_sample(npc_name, voice_sample_path, accent=None):
    if npc_name in sample_mappings:
        sample_mappings[npc_name]["voice_sample"] = voice_sample_path
        if accent:
            sample_mappings[npc_name]["accent"] = accent
    else:
        sample_mappings[npc_name] = {"voice_sample": voice_sample_path, "accent": accent}
    await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
