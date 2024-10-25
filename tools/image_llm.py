"""Generate image from sentences."""
"""Using google text to speech API to generate audio files for the words"""
import argparse
import hashlib
import json
import random
import time
import urllib
import urllib.request
from pathlib import Path
import logging
import itertools


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt_root", type=Path)
    parser.add_argument("out_root", type=Path)
    parser.add_argument("--api", type=str, required=True, help="ComfyUI host URL")
    parser.add_argument("--prompt-json", type=Path, required=True, help="Prompt JSON file for ComfyUI")
    args = parser.parse_args()

    comfyui_prompt_json = json.dumps({"prompt": json.loads(args.prompt_json.read_text())})

    args.out_root.mkdir(parents=True, exist_ok=True)
    
    # We will keep 2 prompts in the queue at a time to avoid overloading the server with too many prompts,
    # But also to keep the server busy by always having a prompt to work on, which (hopefully) prevents unloading of the model.
    queue = []


    def retrieve(prompt_id: str, text_raw: str, text_prompt: str, save_to: Path):
        for i in itertools.count():
            try:
                resp_history = json.loads(urllib.request.urlopen(f"{args.api}/history/{prompt_id}").read())
                image_info = next(iter(resp_history[prompt_id]['outputs'].values()))['images'][0]
                break
            except KeyError:
                # Prompt is still running. Wait a bit
                if i > 180:
                    logging.error(f"Prompt is still running after 180 seconds. Quitting ...")
                    return
                logging.debug(f"Waiting for the prompt to finish... (retrying {i: >2})")
                time.sleep(1)
                continue

        # Download the files from the server
        with urllib.request.urlopen(f"{args.api}/view?{urllib.parse.urlencode(image_info)}") as resp:
            resp = resp.read()
            with open(save_to, "wb") as f:
                f.write(resp)
                logging.info(text_raw)
                logging.info(text_prompt)
                logging.info(f"Saved to {save_to}")

    for file in sorted(args.prompt_root.glob("*.json")):
        content = json.loads(file.read_text())
        prompt_text = ', '.join(f"({k}:1.2)" for k in content['keywords']) + ". " + content['description']
        text_raw = content['sentence']
        sentence_id = hashlib.sha256(text_raw.encode('utf8')).hexdigest()

        save_to = args.out_root / f"{sentence_id}.png"
        if save_to.exists():
            continue

        # Generate image from comfyui
        prompt_json = comfyui_prompt_json
        prompt_json = prompt_json.replace("_PROMPT_TEXT_REPLACE_", prompt_text)
        prompt_json = prompt_json.replace("_FILENAME_PREFIX__REPLACE_", sentence_id)
        prompt_json = prompt_json.replace("\"_SEED_\"", str(random.randint(0, 1000000)))
        # logging.debug(f"Raw JSON: {prompt_json}")

        req = urllib.request.Request(f"{args.api}/prompt")
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsonbytes = prompt_json.encode('utf-8')
        req.add_header('Content-Length', len(jsonbytes))
        with urllib.request.urlopen(req, jsonbytes) as resp:
            resp = json.loads(resp.read().decode('utf-8'))

        prompt_id = resp['prompt_id']
        queue.append((prompt_id, text_raw, prompt_text, save_to))

        while len(queue) > 1:
            retrieve(*queue.pop(0))

    while queue:
        retrieve(*queue.pop(0))
        

if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
