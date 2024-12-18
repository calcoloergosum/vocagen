# Example workflow for Hindi learning via English

# `assets/hi/frequency.csv` is parsed from Wikitionary

# Ask LLM to make example sentences
ROOT=assets/ko
LOGLEVEL=DEBUG python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    Korean Hangul "저에겐 여동생이 한 명 있습니다." \
    --max-words 100

# Translate using Google Cloud translate
python tools/translate.py $ROOT/llm $ROOT/translation_en.json --from-lang ko --to-lang en

# Speak aloud the example sentences using Google Cloud TTS
python tools/tts.py \
    $ROOT/translation_en.json \
    $ROOT/audio/ \
    ko en \
    "{'ko': ['ko-KR-Wavenet-A', 'ko-KR-Wavenet-B', 'ko-KR-Wavenet-C', 'ko-KR-Wavenet-D'], 'en': ['en-GB-Studio-C',]}"

# Generate images for each word using ComfyUI
LOGLEVEL=DEBUG python tools/image.py $ROOT/translation_en.json $ROOT/image/ \
    --use to \
    --prompt-json assets/comfyui.json \
    --additional-prompt "Shot taken with cinematic mise-en-scène in Korea, from far with intricate details, vibrant color. Young and attractive." \
    --api "http://localhost:8188"


# Merge the audio file so that it is nicer to listen to
# python tools/merge_audio.py $ROOT/translation_en.json $ROOT/audio/ $ROOT/audio_per_word/
