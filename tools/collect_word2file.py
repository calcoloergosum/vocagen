import pathlib
import json
import collections


word2locinfo = collections.defaultdict(list)
for p in pathlib.Path("assets/en-hi/llm").glob("*.json"):
    d = json.loads(p.read_text())
    for i_s, s in enumerate(d['sentences']):
        for i_w, w in enumerate(s['en'].split(" ")):
            w = (
                w.lower()
                .replace(",", "")
                .replace(".", "")
                .replace("!", "")
                .replace("?", "")
            )
            word2locinfo[w].append((p.name, i_s, i_w))
        for i_w, w in enumerate(s['hi'].split(" ")):
            w = (
                w.lower()
                .replace(",", "")
                .replace(".", "")
                .replace("!", "")
                .replace("?", "")
                .replace("।", "")
            )
            word2locinfo[w].append((p.name, i_s, i_w))

sorted((len(vs), k) for k, vs in word2locinfo.items())
