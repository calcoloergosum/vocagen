import pathlib
import json
import hashlib

langpair2root = {
    "en": {
        "hi": pathlib.Path("assets/en/hi"),
        "ko": pathlib.Path("assets/en/ko"),
        "ja": pathlib.Path("assets/en/ja"),
        "ru": pathlib.Path("assets/en/ru"),
    },
    "ja": {
        "en": pathlib.Path("assets/ja/en"),
    }
}

# L1name -> L2name -> L2sentence -> L1sentence
L1_2_L2_2sentences = {
    l1: {
        l2: json.loads((root / f"translation_{l1}.json").read_text())
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}
L1_2_L2_2sentences_keys = {
    l1: {
        l2: sorted(L1_2_L2_2sentences[l1][l2].keys(), key=lambda x: (len(x), x))
        for l2 in L1_2_L2_2sentences[l1]
    }
    for l1 in L1_2_L2_2sentences
}

L1_2_L2_2words = {
    l1: {
        l2: sorted((root / 'llm').glob("*"))
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}
L1_2_L2_2images = {
    l1: {
        l2: sorted((root / 'image-horizontal').glob(f"*.png")) + sorted((root / 'image-vertical').glob(f"*.png"))
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}

def sentence2id(s):
    return hashlib.sha256(s.encode('utf8')).hexdigest()
