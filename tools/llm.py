import pandas as pd
import tqdm
import json

from pathlib import Path
from openai import OpenAI
import argparse
import logging


def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frequency_csv", type=Path)
    parser.add_argument("save_to", type=Path, help="Suggested format: $ROOT/$LANG_CODE/llm")
    parser.add_argument("name_L1", type=str, help="Name of L1 language. e.g. English, Hindi, ...")
    parser.add_argument("name_L2", type=str, help="Name of L2 language. e.g. English, Hindi, ...")
    parser.add_argument("code_L1", type=str, help="Language code of L1 language. e.g. en, hi, ko, ja, ...")
    parser.add_argument("code_L2", type=str, help="Language code of L2 language. e.g. en, hi, ko, ja, ...")
    parser.add_argument("script_L1", type=Path, help="Name of script in L1 language. e.g. Alphabet, Devanagari, Hangul, ...")
    parser.add_argument("script_L2", type=Path, help="Name of script in L2 language. e.g. Alphabet, Devanagari, Hangul, ...")
    parser.add_argument("word_L1", type=str)
    parser.add_argument("word_L2", type=str)
    parser.add_argument("sentence_L1", type=str)
    parser.add_argument("sentence_L2", type=str)

    args = parser.parse_args()
    args.save_to.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    df = pd.read_csv(args.frequency_csv)
    for i in tqdm.tqdm(range(0, len(df))):
        rank, frequency, word_foreign, word_transliteration = df.iloc[i]
        save_to = args.save_to / f"{rank:0>5}.json"
        if save_to.exists():
            continue
        query_str = (
            f'The word "{word_foreign} ({word_transliteration})" is {ordinal(rank)} most used word in {args.name_L2}. ' +
            'Could you make 10 simple and short example sentences using this word? ' +
            f'Prefer modern {args.name_L2}, rather than old {args.name_L2}. ' +
            f'Please provide {args.name_L2} sentences in {args.script_L2}, ' +
            f'and {args.name_L1} translation in {args.script_L1} as well, in JSON format. ' +
            f'For example, {{"word": ' +
                f'{{"{args.code_L1}": "{args.word_L1}", ' +
                f'"{args.code_L2}": "{args.word_L2}"}}, ' +
                f'"sentences": [{{"{args.code_L1}": "{args.sentence_L1}",' +
                f'"{args.code_L2}": "{args.sentence_L2}"}}, ...]}}'
        )
        logging.debug(f"LLM: {query_str}")
        for _ in range(3):  # max try 3 times
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": query_str}
                ]
            )
            reply = completion.choices[0].message.content
            try:
                _ = json.loads(reply)
                break
            except json.decoder.JSONDecodeError:
                logging.info(f"Trying again after failing to parse JSON: {reply}")
                continue
        else:
            logging.error(f"Failed to parse JSON after 3 tries: {reply}. Something is wrong.")
            return
        save_to.write_text(reply)


if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
