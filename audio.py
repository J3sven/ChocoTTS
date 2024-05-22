from pydub import AudioSegment
from pydub.playback import play
from concurrent.futures import ThreadPoolExecutor
from shutil import which

AudioSegment.converter = which("ffmpeg")

executor = None

def adjust_volume(sound, volume_change_db):
    return sound + volume_change_db

def audio_player(audio_queue, volume_change_db):
    while True:
        audio_path = audio_queue.get()
        if audio_path is None:
            audio_queue.task_done()
            break
        try:
            sound = AudioSegment.from_wav(audio_path)
            sound = adjust_volume(sound, volume_change_db)
            play(sound)
        finally:
            audio_queue.task_done()

def start_audio_player(audio_queue, volume_change_db):
    global executor
    if executor is None or executor._shutdown:
        executor = ThreadPoolExecutor()
    executor.submit(audio_player, audio_queue, volume_change_db)

def stop_audio_player(audio_queue):
    global executor
    audio_queue.put(None)
    executor.shutdown(wait=True)

