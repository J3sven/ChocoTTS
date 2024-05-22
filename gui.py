import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext
import json
from audio import set_current_volume
from logger import log_message, get_log_messages

class Application(ttk.Window):
    def __init__(self):
        super().__init__(title="TextToTalk WebSocket Interpreter", themename="superhero", size=(600, 400))

        self.status_label = ttk.Label(self, text="Status: Inactive", bootstyle=DANGER)
        self.status_label.pack(pady=10)

        self.uri_label = ttk.Label(self, text="WebSocket URI:", bootstyle=PRIMARY)
        self.uri_label.pack(pady=5)
        self.uri_entry = ttk.Entry(self)
        self.uri_entry.pack(pady=5, fill=X, padx=10)

        control_frame = ttk.Frame(self)
        control_frame.pack(side=BOTTOM, fill=X, pady=10, padx=10, anchor='e')

        self.start_button = ttk.Button(control_frame, text="Start", command=self.start, bootstyle=SUCCESS)
        self.start_button.pack(side=LEFT, padx=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop, bootstyle=DANGER, state="disabled")
        self.stop_button.pack(side=LEFT, padx=5)

        self.volume_label = ttk.Label(control_frame, text="Volume:", bootstyle=PRIMARY)
        self.volume_label.pack(side=LEFT, padx=5)
        self.volume_slider = ttk.Scale(control_frame, from_=0, to=10, orient=HORIZONTAL, command=self.on_volume_change)
        self.volume_slider.pack(side=LEFT, padx=5)

        self.text_area = scrolledtext.ScrolledText(self, wrap='word', width=70, height=20)
        self.text_area.pack(pady=10, fill=BOTH, expand=True)

        self.text_area.tag_configure('even', background='#2b3e50')
        self.text_area.tag_configure('odd', background='#32465a')

        self.start_callback = None
        self.stop_callback = None

        self.message_count = 0

        self.load_settings()
        self.update_log_area()
        
    def log(self, message):
        log_message(message)

    def start(self):
        if self.start_callback:
            self.log("Initializing...")
            self.start_callback()
        self.update_status("Initializing")

    def stop(self):
        if self.stop_callback:
            self.stop_callback()
        self.update_status("Inactive")

    def set_start_callback(self, callback):
        self.start_callback = callback

    def set_stop_callback(self, callback):
        self.stop_callback = callback

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")
        if status == "Active":
            self.status_label.config(bootstyle=SUCCESS)
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        elif status == "Inactive":
            self.status_label.config(bootstyle=DANGER)
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
        elif status == "Initializing":
            self.status_label.config(bootstyle=WARNING)
            self.start_button.config(state="disabled")
            self.stop_button.config(state="disabled")
        elif status == "Error":
            self.status_label.config(bootstyle=PRIMARY)
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def disable_buttons(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")

    def enable_buttons(self):
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def get_uri(self):
        return self.uri_entry.get()

    def get_volume(self):
        return int(self.volume_slider.get())

    def on_volume_change(self, event):
        volume = self.get_volume()
        set_current_volume(volume)

    def load_settings(self):
        try:
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.uri_entry.insert(0, settings.get('websocket_uri', ''))
                self.volume_slider.set(settings.get('volume', 5))
                set_current_volume(settings.get('volume', 5))
        except FileNotFoundError:
            pass

    def save_settings(self):
        settings = {
            'websocket_uri': self.get_uri(),
            'volume': self.get_volume()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)

    def update_log_area(self):
        messages = get_log_messages()
        for message in messages:
            tag = 'even' if self.message_count % 2 == 0 else 'odd'
            self.text_area.insert('end', message + "\n", tag)
            self.text_area.see('end')
            self.message_count += 1
        self.after(100, self.update_log_area)