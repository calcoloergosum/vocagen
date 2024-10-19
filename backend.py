import flask
import hashlib
import warnings
import flask_cors


def format_dict_keys(d):
    """Converts dict keys from snake_case to camelCase."""
    if isinstance(d, dict):
        return {snake_to_camel(k): format_dict_keys(v) for k, v in d.items()}
    if isinstance(d, list):
        return [format_dict_keys(v) for v in d]
    return d


def snake_to_camel(s):
    """
    >>> snake_to_camel("hello_world")
    'helloWorld'
    """
    res = []
    for i, _s in enumerate(s.split("_")):
        res.append(_s.title() if i > 0 else _s.lower())
    return "".join(res)


def sentence2id(s):
    return hashlib.sha256(s.encode('utf8')).hexdigest()


import json
import pathlib
import random

langpair2root = {
    "en": {
        "hi": pathlib.Path("assets/hi"),
    }
}

L1_2_L2_2sentences = {
    l1: {
        l2: json.loads((root / "sentences.json").read_text())
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}

L1_2_L2_2images = {
    l1: {
        l2: sorted((root / 'image').glob(f"*.png"))
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.route('/api/getSupportedLanguagePairs')
def getSupportedLanguages():
    return flask.jsonify(format_dict_keys({
        "pairs": [{"L2": 'hi', "L1": 'en'},]
    }))


@app.route('/api/sentence/<string:L1>/<string:L2>/random')
def random_sentence(L1: str, L2: str):
    """Return random sentence pair from L2 to L1."""
    ss_L2_to_L1 = L1_2_L2_2sentences[L1][L2]
    s_L2 = random.choice(list(ss_L2_to_L1))
    s_L1 = ss_L2_to_L1[s_L2]
    id_L1 = sentence2id(s_L1)
    id_L2 = sentence2id(s_L2)
    audio_L1s = sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L1}_*.mp3"))
    if len(audio_L1s) == 0:
        raise FileNotFoundError(f"Audio file for {id_L1} not found.")
    if len(audio_L1s) != 1:
        warnings.warn(f"Found {len(audio_L1s)} audio files for {id_L1}, expected 1.")
    audio_L1 = audio_L1s[0]

    return flask.jsonify(format_dict_keys({
        "id": id_L2,
        "id_L1": id_L1,
        "id_L2": id_L2,
        "L1": L1,
        "L2": L2,
        "sentence1": s_L1,
        "sentence2": s_L2,
        "audio_urls": [
            app.url_for('audio', L1=L1, L2=L2, id=audio_L1.stem),
            *[
                app.url_for('audio', L1=L1, L2=L2, id=p.stem)
                for p in sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L2}_*.mp3"))
            ]
        ],
        "image_url": app.url_for('image', **dict(zip(["L1", "L2", "id"], filepath_image(L1, L2, id_L1)[1]))),
    }))


@app.route('/api/audio/<string:L1>/<string:L2>/<string:id>')
def audio(L1: str, L2: str, id: str):
    return flask.send_file(langpair2root[L1][L2] / 'audio' / f"{id}.mp3")


@app.route("/api/image/<string:L1>/<string:L2>/<string:id>")
def image(L1: str, L2: str, id: str):
    filepath, _ = filepath_image(L1, L2, id)
    return flask.send_file(filepath)


def filepath_image(L1, L2, idL1):
    filepath = langpair2root[L1][L2] / 'image' / f"{idL1}.png"
    if filepath.exists():
        return (filepath, (L1, L2, idL1))
    else:
        print(f"File not found {filepath}. Fallback to random image.")
        filepath = random.choice(L1_2_L2_2images[L1][L2])
        return filepath, (L1, L2, filepath.stem)


@app.route("/api/report", methods=["POST"])
def report_issue():
    data = flask.request.json
    # For now, just remove the image
    L1, L2 = data["l1"], data["l2"]

    try:
        filepath = langpair2root[L1][L2] / 'image' / f"{pathlib.Path(data["imageUrl"]).stem}.png"
        filepath.unlink()
        print(f"Removed {filepath.as_posix()}")
        return "Done"
    except FileNotFoundError:
        print(f"File not found {filepath.as_posix()}.")
        return flask.Response(status=404)


if __name__ == '__main__':
    app.run(port=8000)
