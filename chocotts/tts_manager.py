import os
import hashlib
import random
from TTS.api import TTS
import torch
from transformers import pipeline
from config import CACHE_DIR, GENERIC_MALE_DIR, GENERIC_FEMALE_DIR, MAPPINGS_FILE_PATH
from mappings import sample_mappings, save_mappings
from logger import log_message

class TTSManager:
    _instance = None

    def __init__(self):
        if TTSManager._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TTSManager._instance = self

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.coqui_tts = None
        self.emotion_classifier = None

    @staticmethod
    def get_instance():
        if TTSManager._instance is None:
            TTSManager()
        return TTSManager._instance

    def initialize_tts_models(self):
        log_message(f"Initializing TTS models on {self.device}...")
        try:
            self.coqui_tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            log_message("TTS model initialized successfully.")
        except Exception as e:
            log_message(f"Error initializing TTS model: {e}")
            self.coqui_tts = None

        try:
            self.emotion_classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)
            log_message("Emotion classifier initialized successfully.")
        except Exception as e:
            log_message(f"Error initializing emotion classifier: {e}")
            self.emotion_classifier = None

    def get_tts(self):
        return self.coqui_tts

    def get_emotion_classifier(self):
        return self.emotion_classifier

    def normalize_npc_name(self, npc_name):
        normalized_name = npc_name.replace(" ", "_").replace("'", "")
        print(f"Raw NPC name: {npc_name}, Normalized NPC name: {normalized_name}")
        return normalized_name

    def infer_emotion(self, text):
        if self.emotion_classifier is None:
            return 'neutral'
        result = self.emotion_classifier(text)
        print(f"Emotion classification result: {result}")
        if result and isinstance(result, list) and len(result) > 0:
            top_result = result[0]
            if isinstance(top_result, dict) and 'label' in top_result:
                return top_result['label']
        return 'neutral'

    def get_cache_path(self, npc_name, text):
        hash_object = hashlib.md5(text.encode())
        file_name = f"{hash_object.hexdigest()}.wav"
        npc_cache_dir = os.path.join(CACHE_DIR, npc_name)
        if not os.path.exists(npc_cache_dir):
            os.makedirs(npc_cache_dir, exist_ok=True)
        return os.path.join(npc_cache_dir, file_name)

    async def get_speaker_info(self, npc_name, voice_gender):
        if npc_name in sample_mappings:
            info = sample_mappings[npc_name]
            speaker_id = info.get("speaker_id", "")
            voice_sample = info.get("voice_sample", None)
            accent = info.get("accent", None)
            return speaker_id, voice_sample, accent

        sample_dir = GENERIC_MALE_DIR if voice_gender.lower() == "male" else GENERIC_FEMALE_DIR
        voice_samples = os.listdir(sample_dir)

        selected_sample = os.path.join(sample_dir, random.choice(voice_samples))
        sample_mappings[npc_name] = {"voice_sample": selected_sample}
        await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
        return "", selected_sample, None

    async def update_voice_sample(self, npc_name, voice_sample_path, accent=None):
        if npc_name in sample_mappings:
            sample_mappings[npc_name]["voice_sample"] = voice_sample_path
            if accent:
                sample_mappings[npc_name]["accent"] = accent
        else:
            sample_mappings[npc_name] = {"voice_sample": voice_sample_path, "accent": accent}
        await save_mappings(sample_mappings, MAPPINGS_FILE_PATH)
