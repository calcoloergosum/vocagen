import json
import logging
import os
import pathlib
import random
import warnings

import flask
import flask_login
import vocagen
from .types import User
from . import dbutils, resource_util


IS_DEVEL = os.environ.get('FLASK_ENV', 'production').lower() == 'development'
if IS_DEVEL:
    print("Launching in development mode.")
    app = flask.Flask(__name__, static_folder='frontend/public')
else:
    app = flask.Flask(__name__, static_folder='frontend/build')
app.secret_key = pathlib.Path("secret_key.txt").read_text().strip()
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


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


@app.route('/api/getSupportedLanguagePairs')
def getSupportedLanguages():
    return flask.jsonify(format_dict_keys({
        "pairs": [
            {"L1": L1, "L2": L2}
            for L1, L2s in resource_util.langpair2root.keys()
            for L2 in L2s
        ]
    }))


@app.route('/api/sentence/<string:L1>/<string:L2>/random')
def random_sentence(L1: str, L2: str):
    """Return random sentence pair from L2 to L1."""
    # Update user statistics
    if flask_login.current_user:
        dbutils.update_user_statistics(flask_login.current_user,
                                    {"per_language_pair": {L1: {L2: {"n_sentences": 1}}}})
    # Update user statistics done
    
    # update seed
    try:
        seed = flask.request.args.get('seed', None)
        print(seed)
        if seed is None:
            seed = random.getrandbits(64)
        else:
            s = int(seed, 16)
    except ValueError:
        logging.warning("Wrong value. Use random seed.")
        s = random.getrandbits(64)
    except TypeError:
        logging.warning("Wrong type. Use random seed.")
        s = random.getrandbits(64)
    rlcg = vocagen.ReversibleRandom(s)
    action = flask.request.args.get('action', 'next')
    v = rlcg.next() if action == 'next' else rlcg.prev()

    s_L2 = resource_util.L1_2_L2_2sentences_keys[L1][L2][int(v % len(resource_util.L1_2_L2_2sentences[L1][L2]))]
    sentence = load_sentence(L1, L2, s_L2)
    return flask.jsonify(format_dict_keys({
        'sentence': sentence,
        'state': hex(v)[2:],
    }))


@app.route('/api/sentence/<string:L1>/<string:L2>/length')
def length_sorted_sentence(L1: str, L2: str):
    """Return n'th longest sentence pair."""
    # Update user statistics
    if flask_login.current_user:
        dbutils.update_user_statistics(flask_login.current_user,
                                    {"per_language_pair": {L1: {L2: {"n_sentences": 1}}}})
    # Update user statistics done

    # update seed
    try:
        seed = flask.request.args.get('seed', None)
        if seed is None:
            seed = random.getrandbits(64)
        else:
            s = int(seed, 16)
    except ValueError:
        logging.warning("Wrong value. Use random seed.")
        s = random.getrandbits(64)
    except TypeError:
        logging.warning("Wrong type. Use random seed.")
        s = random.getrandbits(64)
    action = flask.request.args.get('action', 'next')
    v = s + 1 if action == 'next' else s - 1

    resource_util.L1_2_L2_2sentences_keys[L1][L2][int(s % len(resource_util.L1_2_L2_2sentences[L1][L2]))]
    s_L2 = resource_util.L1_2_L2_2sentences_keys[L1][L2][int(s % len(resource_util.L1_2_L2_2sentences[L1][L2]))]
    sentence = load_sentence(L1, L2, s_L2)
    return flask.jsonify(format_dict_keys({
        'sentence': sentence,
        'state': hex(v)[2:],
    }))


@app.route('/api/word/<string:L1>/<string:L2>/random')
def random_word(L1: str, L2: str):
    """Return random sentence pair from L2 to L1."""
    try:
        seed = flask.request.args.get('seed', None)
        if seed is None:
            seed = random.getrandbits(64)
        else:
            s = int(seed, 16)
    except ValueError:
        logging.warning("Wrong value. Use random seed.")
        s = random.getrandbits(64)
    except TypeError:
        logging.warning("Wrong type. Use random seed.")
        s = random.getrandbits(64)
    rlcg = vocagen.ReversibleRandom(s)
    action = flask.request.args.get('action', 'next')

    for i_try in range(10):  # Try 10 times
        files = resource_util.L1_2_L2_2words[L1][L2]
        v = rlcg.next() if action == 'next' else rlcg.prev()
        wordfile = files[int(v % len(files))]
        worddata = json.loads(wordfile.read_text())

        # Update user statistics
        if flask_login.current_user:
            dbutils.update_user_statistics(flask_login.current_user,
                                        {"per_language_pair": {L1: {L2: {"n_sentences": len(worddata['sentences'])}}}})
        # Update user statistics done

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
        s_L1 = resource_util.L1_2_L2_2sentences[L1][L2][s_L2]
    except KeyError:
        raise FileNotFoundError(f"Translation for {s_L2} not found.")

    id_L1 = resource_util.sentence2id(s_L1)
    id_L2 = resource_util.sentence2id(s_L2)
    audio_L1s = sorted((resource_util.langpair2root[L1][L2] / 'audio').glob(f"{id_L1}_*.mp3"))
    if len(audio_L1s) == 0:
        raise FileNotFoundError(f"Audio file for {id_L1} not found.")
    if len(audio_L1s) != 1:
        warnings.warn(f"Found {len(audio_L1s)} audio files for {id_L1}, expected 1.")
    audio_L1 = audio_L1s[0]

    audio_urls = [
        app.url_for('audio', L1=L1, L2=L2, filename=audio_L1.name),
        *[
            app.url_for('audio', L1=L1, L2=L2, filename=p.name)
            for p in sorted((resource_util.langpair2root[L1][L2] / 'audio').glob(f"{id_L2}_*.mp3"))
        ]
    ]
    if L1 == "en":
        id = id_L1
    elif L2 == "en":
        id = id_L2
    else:
        raise NotImplementedError(f"Unsupported language pair {L1} -> {L2} (Should include English).")

    is_success, _, (l1, l2, filename) = filepath_image(L1, L2, f"{id}.png")
    image_url_horizontal = app.url_for('image_horizontal', L1=l1, L2=l2, filename=filename)
    image_url_vertical = app.url_for('image_vertical', L1=l1, L2=l2, filename=filename)
    return {
        "id_L1": id_L1,
        "id_L2": id_L2,
        "L1": L1,
        "L2": L2,
        "sentence1": s_L1,
        "sentence2": s_L2,
        "audio_urls": audio_urls,
        "image_url_horizontal": image_url_horizontal,
        "image_url_vertical": image_url_vertical,
        "image_is_random": not is_success,
    }

@app.route("/assets/<string:L1>/<string:L2>/image-horizontal/<string:filename>")
def image_horizontal(L1: str, L2: str, filename: str):
    _, filepath, _ = filepath_image(L1, L2, filename)
    return flask.send_file(filepath.absolute(), mimetype='image/png')


@app.route("/assets/<string:L1>/<string:L2>/image-vertical/<string:filename>")
def image_vertical(L1: str, L2: str, filename: str):
    _, filepath, _ = filepath_image(L1, L2, filename)
    filepath2 = pathlib.Path(filepath.as_posix().replace("-horizontal", "-vertical"))
    try:
        return flask.send_file(filepath2.absolute(), mimetype='image/png')
    except FileNotFoundError:
        return flask.send_file(filepath.absolute(), mimetype='image/png')


@login_manager.user_loader
def load_user(email):
    return User(email)


@app.route('/api/statistics')
def statistics():
    if flask_login.current_user:
        return flask.jsonify(format_dict_keys(dbutils.get_user_statistics(flask_login.current_user).to_dict()))
    return flask.redirect(flask.url_for('login'))


@app.route('/api/login', methods=["POST"])
def login():
    # TODO: Implement encryption of hashed password.
    uid = flask.request.json['email']
    password = flask.request.json['password']
    if (user := dbutils.verify_and_get_user(uid, password)):
        if user is None:
            return flask.Response(status=401)
        flask_login.login_user(user)
    return flask.jsonify({"email": uid})


@app.route('/api/register', methods=["POST"])
def register():
    uid = flask.request.json['email']
    password = flask.request.json['password']
    if (user := dbutils.register_credentials(uid, password)):
        flask_login.login_user(user)
        return 'OK'
    return flask.Response(status=400)


def filepath_image(L1, L2, filename: str):
    filepath = resource_util.langpair2root[L1][L2] / 'image-horizontal' / filename
    if filepath.exists():
        return True, filepath, (L1, L2, filename),
    else:
        print(f"File not found {filepath}. Fallback to random image.")
        filepath = random.choice(resource_util.L1_2_L2_2images[L1][L2])
        return False, filepath, (L1, L2, filename),


@app.route("/api/report", methods=["POST"])
def report_issue():
    data = flask.request.json
    # For now, just remove the image
    L1, L2 = data["l1"], data["l2"]
    reason = data['reason']

    filepath = resource_util.langpair2root[L1][L2] / 'image' / f'{pathlib.Path(data["imageUrl"]).stem}.png'
    if not filepath.exists():
        print(f"File not found {filepath.as_posix()}.")
        return flask.Response(status=404)

    if flask_login.current_user:
        dbutils.update_user_statistics(flask_login.current_user, {"n_reports": 1})
        email = flask_login.current_user.email
    else:
        email = 'anonymous'

    with pathlib.Path("reported.txt").open("a") as f:
        f.write(f"{email} {filepath.as_posix()},{reason}\n")
    return "Done"


@app.route('/assets/<string:L1>/<string:L2>/audio/<string:filename>')
def audio(L1: str, L2: str, filename: str):
    # In production, nginx should serve the static files.
    if not IS_DEVEL:
        raise ValueError("This should not be called in production.")
    return flask.send_from_directory(
        (resource_util.langpair2root[L1][L2] / 'audio').absolute(), filename,
        mimetype="audio/mp3", conditional=True)


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
