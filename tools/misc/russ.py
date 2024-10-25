import pathlib

lines = pathlib.Path("raw/ru_50k.txt").read_text().splitlines()[:-1]
items = set([l.split("\t")[1] for l in pathlib.Path("raw/rus_news_2022_30K-words.txt").read_text().splitlines()])
with pathlib.Path("assets/ru/frequency.csv").open("w") as f:
    print("rank,frequency,word,word2", file=f)
    for i, l in enumerate(lines[:10000]):
        name, freq = l.split(" ")
        if name in items:
            print(f"{i+1},{freq},{name},{name}", file=f)
