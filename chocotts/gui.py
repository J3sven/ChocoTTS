import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import scrolledtext, PhotoImage, Label
import json
from audio import set_current_volume
from logger import log_message, get_log_messages

class Application(ttk.Window):
    def __init__(self):
        super().__init__(title="ChocoTTS", themename="superhero", size=(600, 400))

        self.iconbitmap("chocotts/assets/chocotts.ico")

        self.status_label = ttk.Label(self, text="Status: Inactive", bootstyle=DANGER)
        self.status_label.pack(pady=10)

        uri_frame = ttk.Frame(self)
        uri_frame.pack(pady=5, padx=10, fill=X)

        self.uri_label = ttk.Label(uri_frame, text="WebSocket URI:", bootstyle=PRIMARY)
        self.uri_label.grid(row=0, column=0, padx=5, pady=5)
        self.uri_entry = ttk.Entry(uri_frame)
        self.uri_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        uri_frame.grid_columnconfigure(1, weight=1)

        control_frame = ttk.Frame(self)
        control_frame.pack(side=BOTTOM, fill=X, pady=10, padx=10)

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=0, column=0, padx=5)

        self.start_button = ttk.Button(button_frame, text="Start", command=self.start, bootstyle=SUCCESS)
        self.start_button.pack(side=LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop, bootstyle=DANGER, state="disabled")
        self.stop_button.pack(side=LEFT, padx=5)

        volume_frame = ttk.Frame(control_frame)
        volume_frame.grid(row=0, column=1, padx=5, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1)


        volume_frame = ttk.Frame(control_frame)
        volume_frame.grid(row=0, column=1, padx=65, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1)

        volume_inner_frame = ttk.Frame(volume_frame)
        volume_inner_frame.pack(side=LEFT, fill=X, expand=True)

        self.volume_label = ttk.Label(volume_inner_frame, text="Volume:", bootstyle=PRIMARY)
        self.volume_label.pack(side=LEFT, padx=5)
        self.volume_slider = ttk.Scale(volume_inner_frame, from_=0, to=10, orient=HORIZONTAL, command=self.on_volume_change)
        self.volume_slider.pack(side=LEFT, fill=X, expand=True)

        logo_frame = ttk.Frame(control_frame)
        logo_frame.grid(row=0, column=2, padx=5)

        self.logo_image = PhotoImage(file="chocotts/assets/chocobo.png")
        self.logo_label = Label(logo_frame, image=self.logo_image)
        self.logo_label.pack(side=RIGHT, padx=5)

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
            with open('chocotts/settings/settings.json', 'r') as f:
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
        with open('chocotts/settings/settings.json', 'w') as f:
            json.dump(settings, f)

    def update_log_area(self):
        messages = get_log_messages()
        for message in messages:
            tag = 'even' if self.message_count % 2 == 0 else 'odd'
            self.text_area.insert('end', message + "\n", tag)
            self.text_area.see('end')
            self.message_count += 1
        self.after(100, self.update_log_area)