"""Using google text to speech API to generate audio files for the words"""
import argparse
import ast
import hashlib
import json
from pathlib import Path

import tqdm
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3,
    speaking_rate=1.0,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path, help="json file containing the sentence translations from L2 to L1")
    parser.add_argument("out_root", type=Path)
    parser.add_argument("L2", type=str)
    parser.add_argument("L1", type=str)
    parser.add_argument("google_lang_code2names", type=ast.literal_eval,
                        help='Lang code to voice dictionary. ' +
                        'e.g. {"hi": ["hi-IN-Wavenet-A", "hi-IN-Wavenet-E",], "en": ["en-US-Wavenet-H",]}. ' +
                        'For available options, refer to https://cloud.google.com/text-to-speech/docs/voices.'
    )
    args = parser.parse_args()
    args.out_root.mkdir(parents=True, exist_ok=True)

    s2s = json.loads(args.json.read_text())
    for s_L2, s_L1 in tqdm.tqdm(sorted(s2s.items())):
        lang_code2s = {args.L2: s_L2, args.L1: s_L1}
        for lang_code, names in args.google_lang_code2names.items():
            s = lang_code2s[lang_code]
            synthesis_input = texttospeech.SynthesisInput(text=s)
            prefix = hashlib.sha256(s.encode('utf8')).hexdigest()
            for name in names:
                save_to = args.out_root / f"{prefix}_{name}.mp3"
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


if __name__ == '__main__':
    main()
