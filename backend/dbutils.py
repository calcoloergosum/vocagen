"""Mock database"""
import pathlib
from .types import User, LanguagePairStatistics, Statistics
import json


def verify_and_get_user(uid, password):
    try:
        text = pathlib.Path("userdb/credentials.txt").read_text()
    except FileNotFoundError:
        return None

    for l in text.splitlines():
        if l == "":
            continue
        if (uid, password) == l.split(","):
            return User(uid)
    return None


def register_credentials(uid: str, password: str) -> bool:
    if verify_and_get_user(uid, password) is not None:
        return False
    with pathlib.Path("userdb/credentials.txt").open("a") as f:
        f.write(f"{uid},{password}\n")
    return User(uid)

def _get_user_statistics_file(user: User) -> pathlib.Path:
    fileid = user.email.replace("@", ",")  # As "," is not allowed in email
    return pathlib.Path(f"userdb/{fileid}.json")

def get_user_statistics(user: User) -> Statistics:
    try:
        return Statistics.from_dict(json.loads(_get_user_statistics_file(user).read_text()))
    except FileNotFoundError:
        return Statistics.new(user.email)

def update_user_statistics(user: User, data: dict):
    stat = get_user_statistics(user).to_dict()
    _add_nested_counter(stat, data)
    _get_user_statistics_file(user).write_text(json.dumps(stat))
    return

def _add_nested_counter(counter: dict, counter2: dict):
    for k, v in counter2.items():
        if isinstance(v, dict):
            _add_nested_counter(counter.setdefault(k, {}), v)
        else:
            counter[k] = counter.get(k, 0) + v
