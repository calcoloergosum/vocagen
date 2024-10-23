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
import tqdm


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
    
    # We will keep 2 prompts in the queue at a time to avoid overloading the server with too many prompts,
    # But also to keep the server busy by always having a prompt to work on, which (hopefully) prevents unloading of the model.
    queue = []


    def retrieve(prompt_id: str, save_to: Path):
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
                print(f"Waiting for the prompt to finish... (retrying {i: >2})\r", end="")
                time.sleep(1)
                continue

        # Download the files from the server
        with urllib.request.urlopen(f"{args.api}/view?{urllib.parse.urlencode(image_info)}") as resp:
            resp = resp.read()
            with open(save_to, "wb") as f:
                f.write(resp)
                print(f"Saved to {save_to}")

    s2s = json.loads(args.json.read_text())
    for s_from, s_to in tqdm.tqdm(sorted(s2s.items())):
        text = args.use == 'from' and s_from or s_to
        sentence_id = hashlib.sha256(text.encode('utf8')).hexdigest()
        
        save_to = args.out_root / f"{sentence_id}.png"
        if save_to.exists():
            continue

        # Generate image from comfyui
        prompt_text = comfyui_prompt_text
        prompt_text = prompt_text.replace("_PROMPT_TEXT_REPLACE_", f"({text}:1.2), {args.additional_prompt}")
        prompt_text = prompt_text.replace("_FILENAME_PREFIX__REPLACE_", sentence_id)
        prompt_text = prompt_text.replace("\"_SEED_\"", str(random.randint(0, 1000000)))
        logging.info(f"Prompt: {text}")
        # logging.debug(f"Raw JSON: {prompt_text}")

        req = urllib.request.Request(f"{args.api}/prompt")
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsonbytes = prompt_text.encode('utf-8')
        req.add_header('Content-Length', len(jsonbytes))
        with urllib.request.urlopen(req, jsonbytes) as resp:
            resp = json.loads(resp.read().decode('utf-8'))

        prompt_id = resp['prompt_id']
        queue.append((prompt_id, save_to))

        while len(queue) > 1:
            retrieve(*queue.pop(0))

    while queue:
        retrieve(*queue.pop(0))
        

if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
