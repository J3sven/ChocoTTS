import queue
import threading

log_queue = queue.Queue()
log_lock = threading.Lock()

def log_message(message):
    with log_lock:
        log_queue.put(message)

def get_log_messages():
    messages = []
    while not log_queue.empty():
        with log_lock:
            messages.append(log_queue.get())
    return messages
