import asyncio
import websockets
import json
from tts_manager import TTSManager
import os
from logger import log_message

tts_manager = TTSManager.get_instance()

async def listen_to_server(uri, message_queue, shutdown_event):
    while not shutdown_event.is_set():
        try:
            async with websockets.connect(uri) as websocket:
                log_message("Connected to TextToTalk successfully.")
                while not shutdown_event.is_set():
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        data = json.loads(message)
                        log_message(f"Received message: {data}")
                        await message_queue.put(data)
                    except asyncio.TimeoutError:
                        continue
                    except json.JSONDecodeError as e:
                        print(f"Failed to decode JSON: {e}")
                    except websockets.exceptions.ConnectionClosed as e:
                        log_message(f"Connection closed: {e}")
                        break
                    except Exception as e:
                        log_message(f"An error occurred while receiving message: {e}")
        except asyncio.CancelledError:
            print("listen_to_server task cancelled")
            break
        except Exception as e:
            print(f"Failed to connect or an error occurred: {e}")

        log_message("Reconnecting to TextToTalk...")
        await asyncio.sleep(0.1)
    log_message("Shutting down connection to TextToTalk...")

async def process_messages(message_queue, audio_queue, volume_change_db, shutdown_event):
    while not shutdown_event.is_set():
        try:
            data = await asyncio.wait_for(message_queue.get(), timeout=0.1)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            print("process_messages task cancelled")
            break
        if data is None:
            continue
        try:
            text = data.get("Payload", "")
            npc_name_raw = data.get("Speaker", None)
            voice_sample_path = data.get("VoiceSample", None)
            voice_gender = data.get("Voice", {}).get("Name", "default")
            accent = data.get("Accent", None)

            if npc_name_raw is None:
                print("Speaker name not found in the received data.")
                npc_name = ""
            else:
                npc_name = tts_manager.normalize_npc_name(npc_name_raw)

            if voice_sample_path:
                await tts_manager.update_voice_sample(npc_name, voice_sample_path, accent)

            speaker_id, stored_voice_sample_path, stored_accent = await tts_manager.get_speaker_info(npc_name, voice_gender)
            if not accent:
                accent = stored_accent

            emotion = tts_manager.infer_emotion(text)
            audio_path = tts_manager.get_cache_path(npc_name, text)

            if not os.path.exists(audio_path):
                if stored_voice_sample_path:
                    print(f"Using stored voice sample: {stored_voice_sample_path}")
                    if os.path.exists(stored_voice_sample_path):
                        log_message(f"Before TTS model check: coqui_tts is {'initialized' if tts_manager.get_tts() else 'not initialized'}")
                        if tts_manager.get_tts() is not None:
                            log_message(f"Generating TTS for text: {text}")
                            tts_manager.get_tts().tts_to_file(text=text, speaker_wav=stored_voice_sample_path, language="en", file_path=audio_path)
                        else:
                            log_message("TTS model is not initialized.")
                    else:
                        print(f"Voice sample file not found: {stored_voice_sample_path}. Using default TTS.")
                        if tts_manager.get_tts() is not None:
                            log_message(f"Generating TTS for text: {text}")
                            tts_manager.get_tts().tts_to_file(text=text, emotion=emotion, file_path=audio_path)
                        else:
                            log_message("TTS model is not initialized.")
                else:
                    print("No voice sample provided or stored. Using default TTS.")
                    if tts_manager.get_tts() is not None:
                        log_message(f"Generating TTS for text: {text}")
                        tts_manager.get_tts().tts_to_file(text=text, emotion=emotion, file_path=audio_path)
                    else:
                        log_message("TTS model is not initialized.")
            else:
                print(f"Using cached audio file: {audio_path}")

            print(f"Generated speech saved to {audio_path}")
            audio_queue.put(audio_path)
        except asyncio.CancelledError:
            print("process_messages task cancelled")
            break
        except Exception as e:
            print(f"Failed to process message: {e}")
        finally:
            message_queue.task_done()
    print("Exiting process_messages...")
