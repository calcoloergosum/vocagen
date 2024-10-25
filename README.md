# VocaGen

[Online Demo](voca-gen.com) ... Network bandwidth is limited, please bare with the slowness :)

**This project is currently Work In Progress.**

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
6. Make an audio. I used GCP TTS API.
7. Make a description of image using LLM. I used OpenAI.
8. Make an image. I used local ComfyUI server with FLUX.

After everything is done, run frontend by `cd frontend && npm start`. Also, run backend by `python backend.py`.

### Understanding generation cost

- `sample_ko.sh` generates 100 words, 1000 example sentences, and 5 voices (1 for L1 and 4 for L2).
- Outputs roughly 5 hours of audio.
- Roughly estimated time of execution is 13 minutes without image:
  - sentence generation (LLM): 0.5 seconds / word => 50 seconds,
  - translation: 0.1s / sentence => 100 seconds
  - TTS: 0.1s * #voices / sentence => 500 seconds
- Optionally, generating image adds 3 hours to the estimated time.
  - Image: 10s / sentence => 10,000 seconds

Running the sample generates files with following directory structure:
```
assets
├── hi (the language code name of L2)
│   ├── audio
│   │   ├── (sentence hash + voice names)
│   │   ├── 001815...aafb31_en-US-Wavenet-H.mp3
│   │   ├── ...(4998 more) ...
│   │   └── ffefc2...75e6a6_en-US-Wavenet-H.mp3
│   ├── audio_per_word
│   │   ├── (L1 sentence hashes + ".mp3")
│   │   ├── 001815...aafb31.mp3
│   │   ├── ... (998 more) ...
│   │   └── ffefc2...75e6a6.mp3
│   ├── image
│   │   ├── (L1 sentence hashes + ".png")
│   │   ├── 0051ce...289124.png
│   │   ├── ... (998 more) ...
│   │   └── ffe80f...485ef3.png
│   ├── llm
│   │   ├── ('rank' column value in frequency.csv file + ".json")
│   │   ├── 00001.json
│   │   ├── ... (998 more) ...
│   │   └── 01000.json
│   ├── frequency.csv
│   └── translation_en.json (Translation of L2 into L1 sentences)
├── ko
│   ...
```

## Assets

- English frequency list is generated from [Lancaster University's frequency lists](https://ucrel.lancs.ac.uk/bncfreq/flists.html).
- Hindi frequency list is generated from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Hindi_1900) under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Korean word list is generated from frequecy list of [National Institute of the Korean Language](https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=46&etc_seq=71).
- Japanese frequency list is generated from [BCCWJ frequency list](https://clrd.ninjal.ac.jp/bccwj/en/freq-list.html) under their "educational purpose free usage" license.
- Russian from [OpenSubtitle](https://github.com/hermitdave/FrequencyWords/blob/master/content/2018/ru/ru_50k.txt)
- For more details on how it is processed, refer to `tools/misc`.

## Notes:

- At the beginning, I was trying L2 language acquisition style prompts for LLM. For example, "The word 'एक' is 50th frequently used word in Hindi. Could you make 10 simple and short example sentences using this word? Provide translation in English". I did so because I didn't want another step in pipeline for translation. However, LLM often provides same example sentences and multiple languages made it a bit confused. So I aborted this approach and introduced additional translation step.
- Until `gpt3.5-turbo`, this repo's sample was not working well. Sentences are almost always broken, and given words were often not even used. Such tendency was stronger when it comes to non-Indo-European languages such as Korean or Japanese. Now it seems much better.

## Personal remark

 I was trying to learn Hindi. Learning a language is already hard, but learning Hindi was harder because of lack of study material for an intermediate hobbyist. Every book seemed too easy or too hard. With help of LLM, I believed many fairly minor languages for English speakers can be more intermediate-friendly.

 Also, I strongly believe brute-force memorizing words is both the most effective and efficient way to become advanced user of a language. With [notable exception](https://en.wikipedia.org/wiki/Nigel_Richards_(Scrabble_player)), such approach does not make much sense unless you already know grammatical structures and phonetic features. I personally would first use gamification approach such as Duolingo, then to move to memorizing words.

 Words are easier to recall when it appears in a context. It make sense to me to use example sentences to memorize a word.
