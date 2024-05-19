import os
import json
import aiofiles
import asyncio
from config import MAPPINGS_FILE_PATH

# Function to load NPC to speaker ID mappings from a JSON file
async def load_mappings(file_path):
    if os.path.exists(file_path):
        async with aiofiles.open(file_path, 'r') as file:
            mappings = json.loads(await file.read())
        return convert_old_format(mappings)
    return {}

# Function to save NPC to speaker ID mappings to a JSON file
async def save_mappings(mappings, file_path):
    async with aiofiles.open(file_path, 'w') as file:
        await file.write(json.dumps(mappings, indent=4))

# Function to convert old JSON format to new format
def convert_old_format(mappings):
    converted = {}
    for key, value in mappings.items():
        if isinstance(value, str):
            converted[key] = {"speaker_id": value}
        else:
            converted[key] = value
    return converted

# Load existing mappings from the JSON file
sample_mappings = asyncio.run(load_mappings(MAPPINGS_FILE_PATH))
