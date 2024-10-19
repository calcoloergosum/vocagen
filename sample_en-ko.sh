# Example workflow for Hindi learning from English.
# `assets/hi/frequency.csv` is parsed from Wikitionary
# Ask LLM to make example sentences
# Folder name is two language codes of format L1-L2; e.g. en-hi
ROOT=assets/en-ko
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    English Korean \
    en ko \
    Alphabet Hangul \
    one 하나 \
    "I have a sister." "저에겐 여동생이 한 명 있습니다."

# Speak aloud the example sentences
# For avilable options, https://cloud.google.com/text-to-speech/docs/voices
export GOOGLE_APPLICATION_CREDENTIALS=google-key.json
python tools/tts.py \
    $ROOT/llm/ \
    $ROOT/audio/ \
    "{'ko': ['ko-KR-Wavenet-A', 'ko-KR-Wavenet-B', 'ko-KR-Wavenet-C', 'ko-KR-Wavenet-D'], 'en': ['en-GB-Studio-C',]}"


# Generate images for each word (ComfyUI)
python tools/image.py \
    $ROOT/llm/ \
    $ROOT/image/ \
    --prompt-json assets/comfyui.json \
    --additional-prompt "This pretty photo is taken in Korea." \
    --api "http://192.168.0.9:8188/prompt"

# Merge the audio file so that it is nicer to listen to
python tools/merge_audio.py $ROOT/audio/ $ROOT/audio_per_word/
