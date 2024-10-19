"""Script to convert frequency list from National institute of Korean Language into the format used in this project."""
import pathlib
import re

content = pathlib.Path("raw/niokl.txt").read_text()
lines = [l.split("\t") for l in content.split("\n")][1:-1]
# Line consists of 5 columns: Rank, Word, PoS, Description, Class
# Due to high frequency of homonyms, words include numbers to tell them apart.
pos_interested = ['감', '관', '대', '동', '명', '보', '부', '불', '수', '형']  # No '고', '의'
pos_map = {
    '감': '감탄사',
    '관': '관사',
    '대': '대명사',
    '동': '동사',
    '명': '명사',
    '보': '보조사',
    '부': '부사',
    '불': '부정사',
    '수': '수사',
    '형': '형용사',
}
def replace_func(s):
    return re.sub(r"\d+", '', s)

lines = [[int(100000 if rank == '' else rank), -1, replace_func(word), pos_map[pos]] for rank, word, pos, *_ in lines if pos in pos_interested]
lines = sorted(lines)
content = "rank,frequency,word,pos\n" + '\n'.join([",".join(map(str, l)) for l in sorted(lines)])
res = pathlib.Path("assets/ja-ko/frequency.csv").write_text(content)

print(f"Done! ({res} bytes)")
