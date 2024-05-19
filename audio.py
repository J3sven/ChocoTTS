from pydub import AudioSegment
from pydub.playback import play
from concurrent.futures import ThreadPoolExecutor
from config import VOLUME_CHANGE_DB
from shutil import which

AudioSegment.converter = which("ffmpeg")

# Function to adjust volume of the audio
def adjust_volume(sound, volume_change_db):
    return sound + volume_change_db

# Function to play audio from the queue
def audio_player(audio_queue, volume_change_db):
    while True:
        audio_path = audio_queue.get()
        if audio_path is None:
            break
        sound = AudioSegment.from_wav(audio_path)
        sound = adjust_volume(sound, volume_change_db)
        play(sound)
        audio_queue.task_done()

def start_audio_player(audio_queue):
    executor = ThreadPoolExecutor()
    executor.submit(audio_player, audio_queue, VOLUME_CHANGE_DB)
