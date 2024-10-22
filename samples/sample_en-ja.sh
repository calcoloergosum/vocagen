# Example workflow for English learning via Japanese
# `assets/en/frequency.csv` is parsed from Lancster University frequency list
set -e

# Ask LLM to make example sentences
ROOT=assets/en
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    English Alphabet "I have a sister"

# Translate using Google Cloud translate
python tools/translate.py $ROOT/llm $ROOT/translation_ja.json --from-lang en --to-lang ja

# Speak aloud the example sentences using Google Cloud TTS
# NOTE: 'hi-IN-Wavenet-A' sounds bad. Do not use it.
python tools/tts.py \
    $ROOT/translation_ja.json \
    $ROOT/audio/ \
    ja en \
    "{'ja': ['ja-JP-Neural2-B'], 'en': ['en-US-Wavenet-H','en-AU-Neural2-A','en-GB-Journey-F',]}"

# Generate images for each word using ComfyUI
# This may take a VERY long time
LOGLEVEL=DEBUG python tools/image.py $ROOT/translation_ja.json $ROOT/image/ \
    --use to \
    --prompt-json assets/comfyui.json \
    --additional-prompt "Cinematic photography in India, from far with intricate details, vibrant color. Young and attractive." \
    --api "http://localhost:8188/prompt"


# Merge the audio file so that it is nicer to listen to
# python tools/merge_audio.py $ROOT/translation_ja.json $ROOT/audio/ $ROOT/audio_per_word/
