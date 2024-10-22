# Example workflow for Hindi learning via English
# `assets/hi/frequency.csv` is parsed from Wikitionary
set -e

# Ask LLM to make example sentences
ROOT=assets/hi
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    Hindi Devanagri "मेरे पास एक बहन है।"

# Translate using Google Cloud translate
python tools/translate.py $ROOT/llm $ROOT/translation_en.json --from-lang hi --to-lang en

# Speak aloud the example sentences using Google Cloud TTS
# NOTE: 'hi-IN-Wavenet-A' sounds bad. Do not use it.
python tools/tts.py \
    $ROOT/translation_en.json \
    $ROOT/audio/ \
    hi en \
    "{'hi': ['hi-IN-Neural2-A', 'hi-IN-Neural2-D', 'hi-IN-Wavenet-E'], 'en': ['en-US-Wavenet-H',]}"

# Generate images for each word using ComfyUI
# This may take a VERY long time
LOGLEVEL=DEBUG python tools/image.py $ROOT/translation_en.json $ROOT/image/ \
    --use to \
    --prompt-json assets/comfyui.json \
    --additional-prompt "Cinematic photography in India, from far with intricate details, vibrant color. Young and attractive." \
    --api "http://localhost:8188"


# Merge the audio file so that it is nicer to listen to
# python tools/merge_audio.py $ROOT/translation_en.json $ROOT/audio/ $ROOT/audio_per_word/
