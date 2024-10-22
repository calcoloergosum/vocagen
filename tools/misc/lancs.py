"""Script to convert Lancaster frequency list into the format used in this project."""
import pathlib

content = pathlib.Path("raw/lancs_raw.txt").read_text()
lines = [l.strip().split("\t") for l in content.split("\n")][1:-1]
# Line consists of 3 columns
#     Word = Word type (headword followed by any variant forms) - see pp.4-5
#     PoS  = Part of speech (grammatical word class - see pp. 12-13)
#     Freq = Rounded frequency per million word tokens (down to a minimum of 10 occurrences of a lemma per million)- see pp. 5
# We are only interested in some part of speech.
pos_interested = ["NoC", "Verb", "Adj", "Adv", "Prep", "Conj", "Pron", "DetP", "Ord", "Det", "VMod", "Noun"]

lines = [l for l in lines if l[1] in pos_interested and len(set('0123456789').intersection(l[0])) == 0]
lines = sorted(lines, key=lambda l: int(l[3]), reverse=True)
i_start = 10000
lines = lines[i_start:30000]
content = "rank,frequency,word,pos\n" + '\n'.join([",".join(map(str, [rank + i_start + 1, freq, word, pos])) for rank, (word, pos, freq, *_) in enumerate(lines)])
res = pathlib.Path("assets/en/frequency.csv").write_text(content)

print(f"Done! ({res} bytes)")
