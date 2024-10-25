python tools/story/llm.py assets/ru --max-n 10
python tools/story/translate.py assets/ru/story assets/ru/translation_en.json --from-lang ru --to-lang en
python tools/tts.py \
    assets/ru/translation_en.json \
    assets/ru/audio/ \
    ru en \
    "{'ru': ['ru-RU-Wavenet-A', 'ru-RU-Wavenet-C', 'ru-RU-Wavenet-E',], 'en': ['en-US-Wavenet-H',]}"
