import pathlib

import tqdm
import json
from pydub import AudioSegment
import hashlib


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("json", type=pathlib.Path)
    parser.add_argument("audio_root", type=pathlib.Path)
    parser.add_argument("out_root", type=pathlib.Path)
    args = parser.parse_args()
    args.out_root.mkdir(exist_ok=True, parents=True)

    s2s = json.loads(args.json.read_text())
    for s_L2, s_L1 in tqdm.tqdm(sorted(s2s.items())):
        prefix_L1 = hashlib.sha256(s_L1.encode('utf8')).hexdigest()
        prefix_L2 = hashlib.sha256(s_L2.encode('utf8')).hexdigest()

        # refer file by L1
        save_to = args.out_root / f"{prefix_L1}.mp3"
        if save_to.exists():
            continue

        # Identify the audio files
        audio_l2s = sorted(args.audio_root.glob(f"{prefix_L2}_*.mp3"))
        audio_l1s = sorted(args.audio_root.glob(f"{prefix_L1}_*.mp3"))
        assert len(audio_l1s) == 1
        audio_l1 = audio_l1s[0]

        audio = None
        # speak L1, L2 alternatively
        for f in audio_l2s:
            audio = AudioSegment.from_file(audio_l1) if audio is None else (audio + AudioSegment.from_file(audio_l1))
            # add 1 second pause in between utterances
            audio += AudioSegment.silent(duration=1000)
            audio += AudioSegment.from_file(f)
            audio += AudioSegment.silent(duration=1000)
        # add 5 seconds pause after each words
        audio += AudioSegment.silent(duration=5000)
        audio.export(save_to, format="mp3")


if __name__ == '__main__':
    main()
