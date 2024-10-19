# VocaGen

This project is currently Work In Progress.

Example sentence generation, featuring:
- Audio, Image, example sentences
- Fairly minor languages
- Any level of students: beginners, intermediate, and advanced.
- Full automation (!)
- Web frontend
- Export as audiobook

Screenshot of frontend:

 ![screenshot](assets/screenshot.png)


## Samples

| L1 | L2 | Download Link | Reviewed by | Comment by contributor |
| --- | --- | --- | --- | --- |
| English | Hindi | | | Pretty good, but the language is too pure with no foreign-origin words, which makes it sound a bit off |
| Japanese | English | TODO | | |
| Japanese | Korean | TODO | | This seems very broken |

## Pipeline

Pipeline requires 3 environment variables:
- `$OPENAI_API_KEY`: OpenAI's api key.
- `$GOOGLE_APPLICATION_CREDENTIALS`: Google Cloud Platform's api key.
- `$PROJECT_ID` Google Cloud Platform's Project name for the above credentials.

Sample commands can be found in `samples/sample_*.sh`. Step by step:

1. Prepare words list.
2. Sort by frequency. For each word:
3. Throw it at an LLM to make 10 example sentences. I used OpenAI.
4. Translate the sentences. I used GCP Translate API. For each sentence:
5. Make an image. I used local ComfyUI API.
6. Make an audio. I used GCP TTS API.

After everything is done, run frontend by `cd frontend && npm start`. Also, run backend by `python backend.py`.

Running the sample generates files with following directory structure:
```
assets
├── hi (the language code name of L2)
│   ├── audio
│   │   ├── 001815...aafb31_en-US-Wavenet-H.mp3
│   │   ├── ...(sentence hash + voice names)
│   │   └── ffefc2...75e6a6_en-US-Wavenet-H.mp3
│   ├── audio_per_word
│   │   ├── 001815...aafb31.mp3
│   │   ├── ... (L1 sentence hashes + ".mp3")
│   │   └── ffefc2...75e6a6.mp3
│   ├── image
│   │   ├── 0051ce...289124.png
│   │   ├── ... (L1 sentence hashes + ".png")
│   │   └── ffe80f...485ef3.png
│   ├── llm
│   │   ├── 00001.json
│   │   ├── ... ('rank' column value in frequency.csv file + ".json")
│   │   └── 00661.json
│   ├── frequency.csv
│   └── sentences.json (Translation of L2 into L1 sentences)
├── ko
│   ...
```

## Assets

- Hindi frequency list is generated from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Hindi_1900) under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Korean word list is generated from [National Institute of the Korean Language](https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=46&etc_seq=71).


## Notes:

- At the beginning, I was trying L2 language acquisition style prompts for LLM. For example, "The word 'एक' is 50th frequently used word in Hindi. Could you make 10 simple and short example sentences using this word? Provide translation in English". I did so because I didn't want another step in pipeline for translation. However, LLM often provides same example sentences and multiple languages made it a bit confused. So I aborted this approach and introduced additional translation step.
