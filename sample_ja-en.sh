# Example workflow for English learning from Japanese.
# `assets/en/frequency.csv` is parsed from Wikitionary
# Ask LLM to make example sentences
# Folder name is two language codes of format L1-L2; e.g. ja-en
ROOT=assets/ja-en
LOGLEVEL=INFO python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    Japanese English \
    ja en \
    "Kanji and Kana" Alphabet \
    一 one \
    "ここには一人もいません" "There is nobody here."

# Speak aloud the example sentences
# For avilable options, https://cloud.google.com/text-to-speech/docs/voices
export GOOGLE_APPLICATION_CREDENTIALS=google-key.json
LOGLEVEL=INFO python tools/tts.py \
    $ROOT/llm/ \
    $ROOT/audio/ \
    "{'ja': ['ja-JP-Neural2-B'], 'en': ['en-US-Wavenet-H','en-AU-Neural2-A','en-GB-Journey-F',]}"

# Merge the audio file so that it is nicer to listen to
LOGLEVEL=INFO python tool/merge_audio.py $ROOT/audio/ $ROOT/audio_per_word/
