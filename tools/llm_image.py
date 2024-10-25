import argparse
import json
import logging
from pathlib import Path

import hashlib
import tqdm
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path)
    parser.add_argument("out_root", type=Path)
    parser.add_argument("--use", choices=['from', 'to'])
    args = parser.parse_args()

    args.out_root.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    s2s = json.loads(args.json.read_text())
    for s_from, s_to in tqdm.tqdm(sorted(s2s.items())):
        text = s_from if args.use == 'from' else s_to
        sentence_id = hashlib.sha256(text.encode('utf8')).hexdigest()

        save_to = args.out_root / f"{sentence_id}.json"

        if save_to.exists():
            continue

        query_str = (
            f'Imagine a picture representing a sentence "{text}". ' +
            'what is happening in the picture? ' +
            'Describe with imagery alone without using any text, in 3 keywords and 1 key sentences. ' +
            'Format in JSON with format `{{"keywords": ["word1", "word2", "word3"], "description": "key sentence"}}`'
        )
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
        reply['sentence'] = text
        save_to.write_text(json.dumps(reply))


if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
