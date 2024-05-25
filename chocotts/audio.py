from pydub import AudioSegment
from pydub.playback import play
from concurrent.futures import ThreadPoolExecutor
from shutil import which
import threading

AudioSegment.converter = which("ffmpeg")

executor = None
volume_lock = threading.Lock()
current_volume = 0

def adjust_volume(sound, volume_level):
    if volume_level == 0:
        return sound - 60  # Mute the sound
    else:
        return sound + (volume_level - 5) * 6  # Scale from -30 dB to +30 dB

def set_current_volume(volume):
    global current_volume
    with volume_lock:
        current_volume = volume

def get_current_volume():
    global current_volume
    with volume_lock:
        return current_volume

def audio_player(audio_queue):
    while True:
        audio_path = audio_queue.get()
        if audio_path is None:
            audio_queue.task_done()
            break
        try:
            sound = AudioSegment.from_wav(audio_path)
            sound = adjust_volume(sound, get_current_volume())
            play(sound)
        finally:
            audio_queue.task_done()

def start_audio_player(audio_queue, initial_volume):
    global executor, current_volume
    set_current_volume(initial_volume)
    if executor is None or executor._shutdown:
        executor = ThreadPoolExecutor()
    executor.submit(audio_player, audio_queue)

def stop_audio_player(audio_queue):
    global executor
    audio_queue.put(None)
    executor.shutdown(wait=True)
