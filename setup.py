# setup.py
import sys
import os
from cx_Freeze import setup, Executable

# Temporarily increase the recursion limit
sys.setrecursionlimit(5000)

# Get the absolute paths to the VERSION files
tts_version_file = os.path.join(os.path.abspath('venv/Lib/site-packages/TTS/'), 'VERSION')
trainer_version_file = os.path.join(os.path.abspath('venv/Lib/site-packages/trainer/'), 'VERSION')

# Include additional files
include_files = [
    ('chocotts/settings/settings.json', 'settings/settings.json'),
    ('chocotts/reference_audio/', 'reference_audio'),
    ('chocotts/temp/', 'temp'),
    (tts_version_file, 'TTS/VERSION'),
    (trainer_version_file, 'trainer/VERSION'),
    ('chocotts/assets/chocotts.ico', 'chocotts/assets/chocotts.ico'),
    ('chocotts/main.py', 'main.py'),
    ('chocotts/websocket_handler.py', 'websocket_handler.py'),
    ('chocotts/tts_manager.py', 'tts_manager.py'),
    ('chocotts/gui.py', 'gui.py'),
    ('chocotts/mappings.py', 'mappings.py'),
    ('chocotts/audio.py', 'audio.py'),
    ('chocotts/logger.py', 'logger.py'),
    ('chocotts/config.py', 'config.py')
]

# Dependencies are automatically detected, but it might need fine-tuning.
build_exe_options = {
    # "packages": [
    #     "os", "torch", "transformers", "aiofiles", "pydub", "websockets", "simpleaudio",
    #     "numpy", "scipy", "matplotlib", "librosa", "nltk", "soundfile", "flask", "fsspec",
    #     "pandas", "tqdm", "numba", "unidecode", "spacy", "sklearn", "coqpit", "g2pkk",
    #     "pysbd", "packaging", "inflect", "num2words", "bnnumerizer",
    #     "bnunicodenormalizer", "hangul_romanize", "jamo", "jieba", "pypinyin", "anyascii",
    #     "bangla", "aiohttp", "aiosignal", "annotated_types", "async_timeout",
    #     "attrs", "audioread", "blinker", "blis", "catalogue", "certifi", "cffi",
    #     "charset_normalizer", "click", "cloudpathlib", "colorama", "confection", "contourpy",
    #     "cx_Freeze", "cx_Logging", "cycler", "cymem", "Cython", "dateparser", "decorator",
    #     "docopt", "einops", "encodec", "filelock", "fonttools", "frozenlist", "gruut",
    #     "gruut_ipa", "gruut_lang_de", "gruut_lang_en", "gruut_lang_es", "gruut_lang_fr",
    #     "huggingface_hub", "idna", "itsdangerous", "joblib", "jsonlines", "kiwisolver",
    #     "langcodes", "language_data", "lazy_loader", "lief", "llvmlite", "marisa_trie", "markdown",
    #     "more_itertools", "mpmath", "msgpack", "murmurhash", "networkx",
    #     "platformdirs", "pooch", "preshed", "psutil", "pycparser", "pydantic",
    #     "pydantic_core", "pynndescent", "pyparsing", "pytz", "regex", "requests", "safetensors", 
    #     "six", "smart_open", "soxr", "spacy_legacy", "spacy_loggers", "srsly", "sudachidict_core", "sympy",
    #     "tensorboard", "tensorboard_data_server", "thinc", "threadpoolctl", "tokenizers",
    #     "torchaudio", "trainer", "typeguard", "typer", "typing_extensions", "tzdata",
    #     "tzlocal", "urllib3", "wasabi", "weasel", "werkzeug", "yarl"
    # ],
    "includes": [
        "chocotts.websocket_handler",
        "chocotts.audio",
        "chocotts.config",
        "chocotts.gui",
        "chocotts.logger",
        "chocotts.tts_manager"
    ],
    "excludes": [],
    "include_files": include_files,
    "build_exe": "build_exe_output",
    "optimize": 1,
}

# Base is set to None for console application, "Win32GUI" for a Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name="ChocoTTS",
    version="0.1",
    description="ChocoTTS Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("chocotts/main.py", base=base, icon="chocotts/assets/chocotts.ico")]
)
