import argparse
import json
import logging
from pathlib import Path

import pandas as pd
import tqdm
from openai import OpenAI


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
    parser.add_argument("name", type=str, help="Name of the language. e.g. English, Hindi, ...")
    parser.add_argument("script", type=Path, help="Name of script in the language. e.g. Alphabet, Devanagari, Hangul, ...")
    parser.add_argument("sentence", type=str, help="Example sentence in the language.")
    parser.add_argument("--max-words", type=int, help="Maximum number of words to generate sentences from.", default=1000)

    args = parser.parse_args()
    args.save_to.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    df = pd.read_csv(args.frequency_csv)
    for i in tqdm.tqdm(range(0, min(len(df), args.max_words))):
        rank, frequency, word, word_description = df.iloc[i]
        save_to = args.save_to / f"{rank:0>5}.json"
        if save_to.exists():
            continue
        query_str = (
            f'The word "{word} ({word_description})" is {ordinal(rank)} most used word in {args.name}. ' +
            f'Make 10 simple and short various example sentences in modern {args.name}, written in {args.script} using this word, in JSON format. ' +
            f'For example, {{"sentences": ["{args.sentence}", ...]}}'
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
        reply['word'] = word
        save_to.write_text(json.dumps(reply))


if __name__ == '__main__':
    import os
    LOGLEVEL = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=LOGLEVEL, format="%(asctime)s %(message)s")
    main()
