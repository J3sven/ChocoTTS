# <img src="https://github.com/J3sven/ChocoTTS/blob/main/chocotts/assets/chocotts.png?raw=true" height="56"/> ChocoTTS

ChocoTTS is a WebSocket-based interpreter for the [TextToTalk](https://github.com/karashiiro/TextToTalk) plugin in Dalamud, enabling lifelike text-to-speech (TTS) and emotion inference from text. It uses the 🐸[Coqui Ai TTS](https://github.com/coqui-ai/TTS) model for generating speech and [j-hartmann's emotion transformer model](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) for detecting emotions in text.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Real-time TTS generation using Coqui Ai models, all generated locally
- Emotion inference using j-hartmann's emotion transformer model
- Caching of generated speech for faster repeat access
- Adjustable audio playback volume
- Support for multiple NPCs with different voice samples

## Installation
The application is currently still under development, once a stable version 1.0 is ready and installer will be published.

### Prerequisites

- [XIVLauncher](https://goatcorp.github.io/) (for dalamud)
- [TextToTalk](https://github.com/karashiiro/TextToTalk) (dalamud plugin that will provide us with a websocket server to parse text from)
- Python 3.10 or higher
- [ffmpeg](https://ffmpeg.org/download.html) (for audio processing)
- An NVIDIA GPU is highly recommended


## License
This project is licensed under the GNU General Public License. See the [LICENSE](https://github.com/J3sven/dalamud-texttotalk-websocket-interpreter/blob/main/LICENSE) file for more details.
