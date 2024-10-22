"""Script to convert BCCWJ frequency list into the format used in this project."""
import pathlib
import operator

content = pathlib.Path("raw/bccwj.tsv").read_text()
lines = content.split('\n')[1:-1][1000:2000]
formatter = operator.itemgetter(0, 6, 2, 3)
lines = [formatter(l.split("\t")) for l in lines]
content = "rank,frequency,word,pos\n" + '\n'.join([",".join(map(str, line)) for line in lines])
res = pathlib.Path("assets/ja/frequency.csv").write_text(content)
print(f"Done! ({res} bytes)")
