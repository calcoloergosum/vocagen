"""Using google text to speech API to generate audio files for the words"""
import tqdm
from typing import List, Dict
from pathlib import Path
import json
from google.cloud import texttospeech
import ast

client = texttospeech.TextToSpeechClient()
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=0.8,
)


def on_word(sentences: List[str],
                       google_lang_code2names: Dict[str, List[str]],
                       outpath: Path,
                       prefix: str) -> None:
    outpath.mkdir(parents=True, exist_ok=True)
    for i_sentence, d in enumerate(sentences):
        if len(d) == 0:  # No sentence to convert to audio
            continue

        for lang_code, names in google_lang_code2names.items():
            text = d[lang_code]

            synthesis_input = texttospeech.SynthesisInput(text=text)
            for name in names:
                save_to = outpath / f"{prefix}_{i_sentence:0>2}_{lang_code}_{name}.mp3"
                if save_to.exists():
                    continue

                voice = texttospeech.VoiceSelectionParams(
                    language_code="-".join(name.split("-")[:2]),
                    name=name,
                )
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                    )

                # The response's audio_content is binary.
                with save_to.open("wb") as out:
                    # Write the response to the output file.
                    out.write(response.audio_content)
                    print(f'Audio content written to file "{save_to.as_posix()}"')


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json_root", type=Path)
    parser.add_argument("out_root", type=Path)
    parser.add_argument("google_lang_code2names", type=ast.literal_eval,
                        help='Lang code to voice dictionary. ' +
                        'e.g. {"hi": ["hi-IN-Wavenet-A", "hi-IN-Wavenet-E",], "en": ["en-US-Wavenet-H",]}. ' +
                        'For available options, refer to https://cloud.google.com/text-to-speech/docs/voices.'
    )
    args = parser.parse_args()
    
    for json_file in tqdm.tqdm(sorted(args.json_root.glob("*.json"))):
        word_dict = json.loads(json_file.read_text())
        if isinstance(word_dict, dict):
            pass
        elif isinstance(word_dict, list) and len(word_dict) == 1:
            word_dict = word_dict[0]
        else:
            # Unknown case
            print(word_dict)
            return
        on_word(
            word_dict['sentences'],
            args.google_lang_code2names,
            outpath=args.out_root,
            prefix=f"{json_file.stem}",
        )

if __name__ == '__main__':
    main()
