"""Generate image from sentences."""
"""Using google text to speech API to generate audio files for the words"""
import urllib.request
import tqdm
from typing import List
from pathlib import Path
import json
import urllib
import time
import random


def on_word(api_url: str, sentences: List[str],
            outpath: Path,
            prefix: str,
            comfyui_prompt_text: str,
            additional_prompt: str = "",
            ) -> None:
    outpath.mkdir(parents=True, exist_ok=True)
    for i_sentence, d in enumerate(tqdm.tqdm(sentences, leave=False)):
        if len(d) == 0:  # No sentence to convert to image
            continue

        text = d.get("en", "")
        if text == "":
            continue
        
        id = f"{prefix}_{i_sentence:0>2}"
        save_to = outpath / f"{id}.png"
        if save_to.exists():
            continue

        # Generate image from comfyui
        text += ", " + additional_prompt
        prompt_text = comfyui_prompt_text
        prompt_text = prompt_text.replace("_PROMPT_TEXT_REPLACE_", f"({text}:1.2)")
        prompt_text = prompt_text.replace("_FILENAME_PREFIX__REPLACE_", id)
        prompt_text = prompt_text.replace("_SEED_", str(random.randint(0, 1000000)))

        req = urllib.request.Request(api_url)
        req.add_header('Content-Type', 'application/json; charset=utf-8')
        jsonbytes = prompt_text.encode('utf-8')
        req.add_header('Content-Length', len(jsonbytes))
        with urllib.request.urlopen(req, jsonbytes) as resp:
            resp = json.loads(resp.read().decode('utf-8'))

        prompt_id = resp['prompt_id']
        
        while True:
            try:
                resp_history = json.loads(urllib.request.urlopen(f"http://192.168.0.9:8188/history/{prompt_id}").read())
                image_info = next(iter(resp_history[prompt_id]['outputs'].values()))['images'][0]
                break
            except KeyError:
                # Prompt is still running. Wait a bit
                time.sleep(1)
                continue

        # Download the files from the server
        with urllib.request.urlopen(f"http://192.168.0.9:8188/view?{urllib.parse.urlencode(image_info)}") as resp:
            resp = resp.read()
            with open(save_to, "wb") as f:
                f.write(resp)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json_root", type=Path)
    parser.add_argument("out_root", type=Path)
    parser.add_argument("--additional-prompt", type=str, default="", help="Additional prompt to add to the text")
    parser.add_argument("--api", type=str, required=True, help="ComfyUI endpoint URL")
    parser.add_argument("--prompt-json", type=Path, required=True, help="Prompt JSON file for ComfyUI")
    args = parser.parse_args()

    comfyui_prompt_text = json.dumps({"prompt": json.loads(args.prompt_json.read_text())})
    
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
            args.api,
            word_dict['sentences'],
            outpath=args.out_root,
            prefix=f"{json_file.stem}",
            comfyui_prompt_text=comfyui_prompt_text,
            additional_prompt=args.additional_prompt,
        )

if __name__ == '__main__':
    main()
