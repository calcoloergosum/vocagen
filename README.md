# VocaGen

 I was trying to learn Hindi. Learning a language is already hard, but learning Hindi was harder because of lack of study material. With help of LLM, a language that is widely used but lacks material, can be intermediate-friendly.

 I strongly believe brute-force memorizing words is both the most effective and efficient way to become advanced user of a language. But such approach does not make much sense unless you already know grammatical structure, or phonetic features. I personally would first use gamification approach such as Duolingo, then move to memorizing words. 

 Words are easier to recall when it appears in a context. It make sense to me to use example sentences to memorize a word.

## Samples

| L1 | L2 | Download Link | Reviewed by | Comment by contributor |
| --- | --- | --- | --- | --- |
| English | Hindi | | | Pretty good, but the language is too pure with no foreign-origin words, which makes it sound a bit off |
| Japanese | English | TODO | |
| Japanese | Korean | This is very broken | |

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

## Assets

- Hindi frequency list is generated from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/Hindi_1900) under [CC-BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
- Korean word list is generated from [National Institute of the Korean Language](https://www.korean.go.kr/front/etcData/etcDataView.do?mn_id=46&etc_seq=71).


## Notes:

- At the beginning, I was trying L2 language acquisition style prompts for LLM. For example, "The word 'एक' is 50th frequently used word in Hindi. Could you make 10 simple and short example sentences using this word? Provide translation in English". I did so because I didn't want another step in pipeline for translation. However, LLM often provides same example sentences and multiple languages made it a bit confused. So I aborted this approach and introduced additional translation step.
