import os
from dotenv import load_dotenv

load_dotenv()

# Directory for caching audio files
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# File path for storing NPC to speaker ID mappings
MAPPINGS_FILE_PATH = "sample_mappings.json"

# Generic audio sample directories
GENERIC_MALE_DIR = "reference_audio/generics/male"
GENERIC_FEMALE_DIR = "reference_audio/generics/female"

# Volume change in dB
VOLUME_CHANGE_DB = int(os.getenv("VOLUME_CHANGE_DB", 0))

# WebSocket URI
WS_URI = os.getenv("WEBSOCKET_URI")
