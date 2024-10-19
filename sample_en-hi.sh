# Example workflow for Hindi learning from English.
# `assets/hi/frequency.csv` is parsed from Wikitionary
# Ask LLM to make example sentences
# Folder name is two language codes of format L1-L2; e.g. en-hi
ROOT=assets/en-hi
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    English Hindi \
    en hi \
    Alphabet Devanagri \
    one एक \
    "I have a sister." "मेरे पास एक बहन है।"

# Speak aloud the example sentences
# For avilable options, https://cloud.google.com/text-to-speech/docs/voices
export GOOGLE_APPLICATION_CREDENTIALS=google-key.json
python tools/tts.py \
    $ROOT/llm/ \
    $ROOT/audio/ \
    "{'hi': ['hi-IN-Neural2-A', 'hi-IN-Neural2-D', 'hi-IN-Wavenet-A', 'hi-IN-Wavenet-E'], 'en': ['en-US-Wavenet-H',]}"


# Generate images for each word (ComfyUI)
python tools/image.py \
    $ROOT/llm/ \
    $ROOT/image/ \
    --prompt-json assets/comfyui.json \
    --additional-prompt "Cinematic. India. Thin, attractive." \
    --api "http://192.168.0.9:8188/prompt"

# Merge the audio file so that it is nicer to listen to
python tools/merge_audio.py $ROOT/audio/ $ROOT/audio_per_word/ --image $ROOT/image/
