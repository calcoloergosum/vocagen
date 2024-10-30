import hashlib
import json
import logging
import os
import pathlib
import random
import warnings

import flask

import vocagen


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

L1_2_L2_2sentences = {
    l1: {
        l2: json.loads((root / f"translation_{l1}.json").read_text())
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
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
        l2: sorted((root / 'image').glob(f"*.png")) + sorted((root / 'image_v2').glob(f"*.png"))
        for l2, root in l2_2_root.items()
    }
    for l1, l2_2_root in langpair2root.items()
}

IS_DEVEL = os.environ.get('FLASK_ENV', 'production').lower() == 'development'
if IS_DEVEL:
    print("Launching in development mode.")
    app = flask.Flask(__name__, static_folder='frontend/public')
else:
    app = flask.Flask(__name__, static_folder='frontend/build')

@app.route('/api/getSupportedLanguagePairs')
def getSupportedLanguages():
    return flask.jsonify(format_dict_keys({
        "pairs": [
            {"L1": L1, "L2": L2}
            for L1, L2s in langpair2root.keys()
            for L2 in L2s
        ]
    }))


@app.route('/api/sentence/<string:L1>/<string:L2>/random')
def random_sentence(L1: str, L2: str):
    """Return random sentence pair from L2 to L1."""
    s_L2 = random.choice(list(L1_2_L2_2sentences[L1][L2]))
    s_L1 = L1_2_L2_2sentences[L1][L2][s_L2]
    id_L1 = sentence2id(s_L1)
    id_L2 = sentence2id(s_L2)
    audio_L1s = sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L1}_*.mp3"))
    if len(audio_L1s) == 0:
        raise FileNotFoundError(f"Audio file for {id_L1} not found.")
    if len(audio_L1s) != 1:
        warnings.warn(f"Found {len(audio_L1s)} audio files for {id_L1}, expected 1.")
    audio_L1 = audio_L1s[0]

    audio_urls = [
        app.url_for('audio', L1=L1, L2=L2, filename=audio_L1.name),
        *[
            app.url_for('audio', L1=L1, L2=L2, filename=p.name)
            for p in sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L2}_*.mp3"))
        ]
    ]
    if L1 == "en":
        id = id_L1
    elif L2 == "en":
        id = id_L2
    else:
        raise NotImplementedError(f"Unsupported language pair {L1} -> {L2} (Should include English).")

    is_success, _, l1l2filename = filepath_image(L1, L2, f"{id}.png")
    image_url = app.url_for('image', **dict(zip(["L1", "L2", "filename"], l1l2filename)))
    audio_urls = [url.strip("/") for url in audio_urls]
    image_url = image_url.strip("/")
    return flask.jsonify(format_dict_keys({
        "id": id_L2,
        "id_L1": id_L1,
        "id_L2": id_L2,
        "L1": L1,
        "L2": L2,
        "sentence1": s_L1,
        "sentence2": s_L2,
        "audio_urls": audio_urls,
        "image_url": image_url,
        "image_is_random": not is_success,
    }))


@app.route('/api/word/<string:L1>/<string:L2>/random')
def random_word(L1: str, L2: str):
    """Return random sentence pair from L2 to L1."""
    try:
        s = int(flask.request.args.get('seed', None), 16)
    except ValueError:
        logging.warning("Wrong value. Use random seed.")
        s = random.getrandbits(64)
    except TypeError:
        logging.warning("Wrong type. Use random seed.")
        s = random.getrandbits(64)
    rlcg = vocagen.ReversibleRandom(s)
    action = flask.request.args.get('action', 'next')

    for i_try in range(10):  # Try 10 times
        files = L1_2_L2_2words[L1][L2]
        v = rlcg.next() if action == 'next' else rlcg.prev()
        wordfile = files[int(v % len(files))]
        worddata = json.loads(wordfile.read_text())
        try:
            return flask.jsonify(format_dict_keys({
                'sentences': [load_sentence(L1, L2, s_L2) for s_L2 in worddata['sentences']],
                'word': worddata['word'],
                'state': hex(v)[2:],
            }))
        except FileNotFoundError:
            logging.warning("Failed to load %s. Retry (%s).", wordfile, i_try)
            continue
    raise FileNotFoundError("No valid word found.")


def load_sentence(L1: str, L2: str, s_L2: str):
    try:
        s_L1 = L1_2_L2_2sentences[L1][L2][s_L2]
    except KeyError:
        raise FileNotFoundError(f"Translation for {s_L2} not found.")

    id_L1 = sentence2id(s_L1)
    id_L2 = sentence2id(s_L2)
    audio_L1s = sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L1}_*.mp3"))
    if len(audio_L1s) == 0:
        raise FileNotFoundError(f"Audio file for {id_L1} not found.")
    if len(audio_L1s) != 1:
        warnings.warn(f"Found {len(audio_L1s)} audio files for {id_L1}, expected 1.")
    audio_L1 = audio_L1s[0]

    audio_urls = [
        app.url_for('audio', L1=L1, L2=L2, filename=audio_L1.name),
        *[
            app.url_for('audio', L1=L1, L2=L2, filename=p.name)
            for p in sorted((langpair2root[L1][L2] / 'audio').glob(f"{id_L2}_*.mp3"))
        ]
    ]
    if L1 == "en":
        id = id_L1
    elif L2 == "en":
        id = id_L2
    else:
        raise NotImplementedError(f"Unsupported language pair {L1} -> {L2} (Should include English).")

    is_success, _, l1l2filename = filepath_image(L1, L2, f"{id}.png")
    image_url = app.url_for('image', **dict(zip(["L1", "L2", "filename"], l1l2filename)))
    audio_urls = [url.strip("/") for url in audio_urls]
    image_url = image_url.strip("/")
    return {
        "id_L1": id_L1,
        "id_L2": id_L2,
        "L1": L1,
        "L2": L2,
        "sentence1": s_L1,
        "sentence2": s_L2,
        "audio_urls": audio_urls,
        "image_url": image_url,
        "image_is_random": not is_success,
    }


@app.route('/assets/<string:L1>/<string:L2>/audio/<string:filename>')
def audio(L1: str, L2: str, filename: str):
    return flask.send_from_directory(
        langpair2root[L1][L2] / 'audio', filename,
        mimetype="audio/mp3", conditional=True)


@app.route("/assets/<string:L1>/<string:L2>/image/<string:filename>")
def image(L1: str, L2: str, filename: str):
    _, filepath, _ = filepath_image(L1, L2, filename)
    return flask.send_file(filepath)


def filepath_image(L1, L2, filename: str):
    filepath = langpair2root[L1][L2] / 'image' / filename
    if filepath.exists():
        return True, filepath, (L1, L2, filename),
    else:
        print(f"File not found {filepath}. Fallback to random image.")
        filepath = random.choice(L1_2_L2_2images[L1][L2])
        return False, filepath, (L1, L2, filename),


@app.route("/api/report", methods=["POST"])
def report_issue():
    data = flask.request.json
    # For now, just remove the image
    L1, L2 = data["l1"], data["l2"]
    reason = data['reason']

    filepath = langpair2root[L1][L2] / 'image' / f'{pathlib.Path(data["imageUrl"]).stem}.png'
    if not filepath.exists():
        print(f"File not found {filepath.as_posix()}.")
        return flask.Response(status=404)

    with pathlib.Path("reported.txt").open("a") as f:
        f.write(f"{filepath.as_posix()},{reason}\n")
    return "Done"


if IS_DEVEL:
    print("Development setting")
    import requests
    API_HOST = "http://localhost:3000/"

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Proxy to the frontend server."""
        request = flask.request
        res = requests.request(  # ref. https://stackoverflow.com/a/36601467/248616
            method          = request.method,
            url             = request.url.replace(request.host_url, f'{API_HOST}').replace("/%PUBLIC_URL%", ""),
            headers         = {k:v for k,v in request.headers if k.lower() != 'host'}, # exclude 'host' header
            data            = request.get_data(),
            cookies         = request.cookies,
            allow_redirects = False,
        )

        #region exlcude some keys in :res response
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']  #NOTE we here exclude all "hop-by-hop headers" defined by RFC 2616 section 13.5.1 ref. https://www.rfc-editor.org/rfc/rfc2616#section-13.5.1
        headers          = [
            (k,v) for k,v in res.raw.headers.items()
            if k.lower() not in excluded_headers
        ]
        #endregion exlcude some keys in :res response

        response = flask.Response(res.content, res.status_code, headers)
        return response
else:
    print("production setting")

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return flask.send_from_directory(app.static_folder, path)
        else:
            return flask.send_from_directory(app.static_folder, 'index.html')


@app.route('/health')
def health() -> str:
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001 if IS_DEVEL else 8002)
