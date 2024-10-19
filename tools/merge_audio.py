import pathlib
from pydub import AudioSegment
import tqdm


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_root", type=pathlib.Path)
    parser.add_argument("out_root", type=pathlib.Path)
    args = parser.parse_args()
    args.out_root.mkdir(exist_ok=True, parents=True)

    files = sorted(args.audio_root.glob("*.mp3"))

    # group files by word, sentence, language code
    i_word2i_sentence2lang_code2files = {}
    for f in files:
        i_word, i_sentence, lang_code, speaker_name = f.stem.split("_")
        if i_word not in i_word2i_sentence2lang_code2files:
            i_word2i_sentence2lang_code2files[i_word] = {}
        if i_sentence not in i_word2i_sentence2lang_code2files[i_word]:
            i_word2i_sentence2lang_code2files[i_word][i_sentence] = {}
        if lang_code not in i_word2i_sentence2lang_code2files[i_word][i_sentence]:
            i_word2i_sentence2lang_code2files[i_word][i_sentence][lang_code] = []
        i_word2i_sentence2lang_code2files[i_word][i_sentence][lang_code].append(f)

    for i_word, i_sentence2lang_code2files in tqdm.tqdm(sorted(i_word2i_sentence2lang_code2files.items())):
        save_to = args.out_root / f"{i_word}.mp3"
        if save_to.exists():
            continue
        audio = None
        for i_sentence, lang_code2files in sorted(i_sentence2lang_code2files.items()):
            langs = list(lang_code2files.keys())
            langs.remove('en')
            assert len(langs) == 1
            other_lang = langs[0]
            en_files = lang_code2files.get("en", [])
            if len(en_files) == 0:
                continue
            en_file = en_files[0]
            # speak english, hindi alternatively
            for hi_file in lang_code2files[other_lang]:
                audio = AudioSegment.from_file(en_file) if audio is None else (audio + AudioSegment.from_file(en_file))
                # add 1 second pause in between utterances
                audio += AudioSegment.silent(duration=1000)
                audio += AudioSegment.from_file(hi_file)
                audio += AudioSegment.silent(duration=1000)
        # add 2 seconds pause after each words
        audio += AudioSegment.silent(duration=2000)
        audio.export(save_to, format="mp3")


if __name__ == '__main__':
    main()
