import argparse
import json
import pathlib
from os import environ
import html

import tqdm
from google.cloud import translate


def main():
    llm = pathlib.Path("assets/ru/llm")
    llm.mkdir(parents=True, exist_ok=True)
    image_prompt = pathlib.Path("assets/ru/image_prompt")
    image_prompt.mkdir(parents=True, exist_ok=True)
    translation = json.loads(pathlib.Path("assets/ru/translation_en.json").read_text())

    for p in pathlib.Path("assets/ru/story").glob("*.json"):
        data = json.loads(p.read_text())
        (llm / p.name).write_text(json.dumps({
            "sentences": [s['text'] for s in data["sentences"]],
            "word": data["word"],
        }))
        for i_s, s in enumerate(data['sentences']):
            (image_prompt / f"{p.stem}_{i_s + 1}.json").write_text(json.dumps({
                "keywords": [],
                "description": translation[s["image"]] + ". " + translation[s["text"]],
                "sentence": translation[s["text"]],
            }))
    print("Done")


if __name__ == "__main__":
    main()
