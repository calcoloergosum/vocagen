import argparse
import json
import logging
from pathlib import Path

import pandas as pd
import tqdm
from openai import OpenAI


def ordinal_en(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix


def query_string(rank: int, word: str, word_description: str, langname: str, script: str):
    if langname == 'English':
        sentence = "I have a sister"
        return (
            f'The word "{word} ({word_description})" is {ordinal_en(rank)} most used word in {langname}. ' +
            f'Make 10 simple and short various example sentences in modern {langname}, written in {script} using this word, in JSON format. ' +
            f'For example, {{"sentences": ["{sentence}", ...]}}'
        )
    if langname == 'हिन्दी':
        sentence = "मेरे पास एक बहन है।"
        return (
            f'शब्द "{word} ({word_description})" {langname} में {ordinal_hi(rank)} सबसे ज़्यादा इस्तेमाल किया जाने वाला शब्द है।' +
            f'आधुनिक {langname} में 10 सरल और छोटे उदाहरण वाक्य बनाएँ, जिन्हें JSON फ़ॉर्मेट में इस शब्द का इस्तेमाल करके {script} में लिखा गया है। ' +
            f'उदाहरण के लिए, {{"sentences": ["{sentence}", ...]}}'
        )
    if langname == 'ja':
        sentence = "ここには一人もいません。"
    if langname == 'ko':
        sentence = "저에겐 여동생이 한 명 있습니다."
    raise ValueError(f"Unsupported language: {langname}")


def ordinal_hi(n: int) -> str:
    """Return ordinal number in Hindi.
    >>> ordinal_hi(1)
    पहला
    >>> ordinal_hi(2)
    दूसरा
    >>> ordinal_hi(3)
    तीसरा
    >>> ordinal_hi(4)
    चौथी
    >>> ordinal_hi(5)
    पांचवां
    >>> ordinal_hi(6)
    छठा
    >>> ordinal_hi(7)
    सातवीं
    >>> ordinal_hi(8)
    आठवाँ
    >>> ordinal_hi(9)
    नौवें
    >>> ordinal_hi(10)
    दसवां
    >>> ordinal_hi(11)
    ग्यारहवें
    """
    if n == 1:
        return 'पहला'
    if n == 2:
        return 'दूसरा'
    if n == 3:
        return 'तीसरा'
    if n == 4:
        return 'चौथा'
    if n == 5:
        return 'पांचवां'
    if n == 6:
        return 'छठा'
    if n == 7:
        return 'सातवीं'
    if n == 8:
        return 'आठवाँ'
    if n == 9:
        return 'नौवें'
    if n == 10:
        return 'दसवां'
    return f'{n}वें'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("frequency_csv", type=Path)
    parser.add_argument("save_to", type=Path,
                        help="Suggested format: $ROOT/$LANG_CODE/llm")
    parser.add_argument("name", type=str,
                        help="Name of the language. e.g. English, Hindi, ...")
    parser.add_argument("script", type=Path,
                        help="Name of script in the language. e.g. Alphabet, Devanagari, Hangul, ...")
    parser.add_argument("--max-words", type=int,
                        help="Maximum number of words to generate sentences from.", default=1000)

    args = parser.parse_args()
    args.save_to.mkdir(parents=True, exist_ok=True)

    client = OpenAI()

    df = pd.read_csv(args.frequency_csv)
    for i in tqdm.tqdm(range(0, min(len(df), args.max_words))):
        rank, _, word, word_description = df.iloc[i]  # ignore frequency
        save_to = args.save_to / f"{rank:0>5}.json"
        if save_to.exists():
            continue
        query_str = query_string(rank, word, word_description, args.name, args.script)
        logging.debug("LLM Request: %s", query_str)
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
