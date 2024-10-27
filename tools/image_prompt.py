import argparse
import json
import logging
from pathlib import Path

import tqdm
from openai import OpenAI


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=Path)
    parser.add_argument("out_root", type=Path)
    parser.add_argument("--use", choices=['from', 'to'])
    parser.add_argument("--additional-prompt", type=str, default="", help="Additional prompt to add to the text")
    parser.add_argument("--api", type=str, required=True, help="ComfyUI host URL")
    parser.add_argument("--prompt-json", type=Path, required=True, help="Prompt JSON file for ComfyUI")
    args = parser.parse_args()

    comfyui_prompt_text = json.dumps({"prompt": json.loads(args.prompt_json.read_text())})

    args.out_root.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    s2s = json.loads(args.json.read_text())
    for s_from, s_to in tqdm.tqdm(sorted(s2s.items())):
        text = args.use == 'from' and s_from or s_to
        sentence_id = hashlib.sha256(text.encode('utf8')).hexdigest()
        
        save_to = args.out_root / f"{sentence_id}.json"
        if save_to.exists():
            continue

        query_str = (
            f'Imagine a picture representing a sentence "{text}". ' +
            f'Describe what is happening in the picture in 3 keywords and 1 key sentences.' +
            f'Format in JSON with format `{{"keywords": ["word1", "word2", "word3"], "description": "key sentence"}}`'
        )
        logging.debug(f"LLM Request: {query_str}")
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
                logging.info(f"Trying again after failing to parse JSON: {reply}")
                continue
        else:
            logging.error(f"Failed to parse JSON after 3 tries: {reply}. Something is wrong.")
            return
        logging.debug(f"LLM Reply: {reply}")
        reply = json.loads(reply)
        reply['sentence'] = text
        save_to.write_text(json.dumps(reply))


if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
