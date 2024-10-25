import argparse
import json
import logging
from pathlib import Path

import pandas as pd
import hashlib
import tqdm
from openai import OpenAI
import pathlib


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--max-n", type=int, default=10)
    args = parser.parse_args()

    out_root = args.root / "story"
    out_root.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    df = pd.read_csv(args.root / "frequency.csv")
    for i in tqdm.tqdm(range(0, min(len(df), args.max_n))):
        if i >= args.max_n:
            break

        rank, _, word, _ = df.iloc[i]  # ignore frequency

        save_to = out_root / f"{rank:0>5}.json"

        if save_to.exists():
            continue

        query_str = (args.root / 'story.txt').read_text().replace("_WORD_", word)
        for _ in range(3):  # max try 3 times
            completion = client.chat.completions.create(
                model="gpt-4o-2024-05-13",
                messages=[
                    {"role": "user", "content": query_str}
                ],
                response_format={"type": "json_object"},
            )
            reply = completion.choices[0].message.content
            reply = reply.replace('```json', '').replace('```', '')
            try:
                _ = json.loads(reply)
                break
            except json.decoder.JSONDecodeError:
                logging.info("Trying again after failing to parse JSON: %s", reply)
                continue
        else:
            logging.error("Failed to parse JSON after 3 tries: %s. Something is wrong.", reply)
            return
        logging.debug("LLM Reply: %s", reply)
        reply = json.loads(reply)
        reply['word'] = word
        save_to.write_text(json.dumps(reply))


if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
