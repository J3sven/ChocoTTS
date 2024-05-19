# TextToTalk Websocket Interpreter

A WebSocket interpreter for Dalamud's TextToTalk addon that leverages Coqui Ai TTS for lifelike audio and j-hartmann's emotion transformer model to infer emotion from text.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This project provides a WebSocket-based interpreter for the TextToTalk addon in Dalamud, enabling lifelike text-to-speech (TTS) and emotion inference from text. It uses the 🐸[Coqui Ai TTS](https://github.com/coqui-ai/TTS) model for generating speech and [j-hartmann's emotion transformer model](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) for detecting emotions in text.

## Features

- Real-time TTS generation using Coqui Ai models
- Emotion inference using j-hartmann's emotion transformer model
- Caching of generated speech for faster repeat access
- Adjustable audio playback volume
- Support for multiple NPCs with different voice samples

## Installation

### Prerequisites

- [XIVLauncher](https://goatcorp.github.io/) (for dalamud)
- [TextToTalk](https://github.com/karashiiro/TextToTalk) (dalamud plugin that will provide us with a websocket server to parse text from)
- Python 3.10 or higher
- [ffmpeg](https://ffmpeg.org/download.html) (for audio processing)
- An NVIDIA GPU is highly recommended

### Steps

1. Clone the repository:

   ```sh
   git clone git@github.com:J3sven/dalamud-texttotalk-websocket-interpreter.git
   cd dalamud-texttotalk-websocket-interpreter
   ```
2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Ensure `ffmpeg` is installed and accessible in your system's PATH. On Windows, you might need to set the `ffmpeg` path directly in your script:
   ```
   from pydub.utils import which
   AudioSegment.converter = which("ffmpeg")
   ```
## Usage

1. Create a `.env` file in the root directory of the project and configure it with your desired settings:
   ```sh
   WEBSOCKET_URI=localhost:8765 # Change this to whatever IP:port your TextToTalk plugin is hosting it's websocket server on
   VOLUME_CHANGE_DB=0  # Change this value to adjust the playback volume
   ```
2. Run the main script:
   
   ```sh
   python main.py
   ```

## Project Structure
```
project/
├── cache/                     # Contains previously generated audio files
├── audio_samples/             # Contains audio samples that are used for on-the-fly voice cloning
├── audio.py                   # Handles audio playback and volume adjustment
├── config.py                  # Configuration settings and environment variables
├── main.py                    # Main entry point of the application
├── mappings.py                # Manages loading and saving NPC to speaker ID mappings
├── tts.py                     # Handles text-to-speech processing and emotion detection
├── websocket_handler.py       # Manages WebSocket connections and message processing
├── requirements.txt           # List of required Python packages
├── sample_mappings.json       # Structured data that tells the script what audio sample to use when generating new audio files
└── .env                       # Environment variables configuration
```

## License
This project is licensed under the GNU General Public License. See the [LICENSE](https://github.com/J3sven/dalamud-texttotalk-websocket-interpreter/blob/main/LICENSE) file for more details.
