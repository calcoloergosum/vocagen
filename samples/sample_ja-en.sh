# Example workflow for Japanese learning via English
# `assets/ja/frequency.csv` is parsed from BCCWJ frequency list
set -e

# Ask LLM to make example sentences in English
ROOT=assets/ja
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    Japanese "Kana and Kanji" "ここには一人もいません。"

# Translate using Google Cloud translate
python tools/translate.py $ROOT/llm $ROOT/translation_en.json --from-lang ja --to-lang en

# Speak aloud the example sentences using Google Cloud TTS
python tools/tts.py \
    $ROOT/translation_en.json \
    $ROOT/audio/ \
    ja en \
    "{'ja': ['ja-JP-Neural2-B', 'ja-JP-Wavenet-A', 'ja-JP-Wavenet-B'], 'en': ['en-US-Wavenet-H']}"

# Generate images for each word using ComfyUI
# This may take a VERY long time
LOGLEVEL=DEBUG python tools/image.py $ROOT/translation_en.json $ROOT/image/ \
    --use to \
    --prompt-json assets/comfyui.json \
    --additional-prompt "Cinematic photography in Japan, from far with intricate details, vibrant color. Young and attractive." \
    --api "http://localhost:8188/prompt"


# Merge the audio file so that it is nicer to listen to
# python tools/merge_audio.py $ROOT/translation_en.json $ROOT/audio/ $ROOT/audio_per_word/
