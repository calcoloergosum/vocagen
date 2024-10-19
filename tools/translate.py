import argparse
import json
import pathlib
from os import environ
import html

import tqdm
from google.cloud import translate

# Setting project id for GCP
PROJECT_ID = environ.get("PROJECT_ID", "")
assert PROJECT_ID
PARENT = f"projects/{PROJECT_ID}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("llm", type=pathlib.Path)
    parser.add_argument("save_to", type=pathlib.Path)
    parser.add_argument("--from-lang", type=str)
    parser.add_argument("--to-lang", type=str)
    args = parser.parse_args()

    args.save_to.parent.mkdir(parents=True, exist_ok=True)

    client = translate.TranslationServiceClient()

    try:
        hi2en = json.loads(args.save_to.read_text())
    except FileNotFoundError:
        hi2en = {}

    for p in tqdm.tqdm(sorted(args.llm.glob("*.json"))):
        d = json.loads(p.read_text())
        for s in tqdm.tqdm(d['sentences'], leave=False):
            if s in hi2en:
                continue
            response = client.translate_text(
                contents=[s],
                parent=PARENT,
                source_language_code=args.from_lang,
                target_language_code=args.to_lang,
            )
            text = response.translations[0].translated_text
            # Unescape HTML entities
            text = html.unescape(text)
            hi2en[s] = text

            with args.save_to.open("w") as f:
                json.dump(hi2en, f, indent=2)


if __name__ == "__main__":
    main()
