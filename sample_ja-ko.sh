# Example workflow for English learning from Japanese.
# `assets/en/frequency.csv` is parsed from Wikitionary
# Ask LLM to make example sentences
# Folder name is two language codes of format L1-L2; e.g. ja-en
ROOT=assets/ja-ko
LOGLEVEL=DEBUG python tools/llm.py \
    $ROOT/frequency.csv \
    $ROOT/llm/ \
    Japanese Korean \
    ja ko \
    "Kanji and Kana" Hangul \
    一 하나 \
    "ここには一人もいません" "여기엔 아무도 없습니다."

# Speak aloud the example sentences
# For avilable options, https://cloud.google.com/text-to-speech/docs/voices
export GOOGLE_APPLICATION_CREDENTIALS=google-key.json
LOGLEVEL=INFO python tools/tts.py \
    $ROOT/llm/ \
    $ROOT/audio/ \
    "{'ja': ['ja-JP-Neural2-B'], 'ko': ['ko-KR-Neural2-A', 'ko-KR-Neural2-B']}"

# Merge the audio file so that it is nicer to listen to
LOGLEVEL=INFO python tool/merge_audio.py $ROOT/audio/ $ROOT/audio_per_word/
