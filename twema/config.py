#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import sys
import os.path

import toml
import xdg

config_file_path = xdg.XDG_CONFIG_HOME / "twema" / "config.toml"
oauth_tokens_path = xdg.XDG_DATA_HOME / "twema" / "oauth-tokens"
tweets_db_path = xdg.XDG_DATA_HOME / "twema" / "tweets.db"


def _load():
    try:
        return toml.load(config_file_path)
    except FileNotFoundError:
        return {}


def load():
    data = _load()
    if not isinstance(data.get("mail"), dict) or (
        "from" not in data["mail"] or "to" not in data["mail"]
    ):
        print("mail.from and mail.to are required in " + str(config_file_path))
        sys.exit(1)

    if not isinstance(data.get("app"), dict) or (
        "consumer_key" not in data["app"]
        or "consumer_secret" not in data["app"]
    ):
        print(
            "app.consumer_key and app.consumer_secret are required in "
            + str(config_file_path)
        )
        sys.exit(1)
    return data


def have_oauth_tokens():
    return os.path.exists(oauth_tokens_path)


def prepare_oauth_tokens_file():
    oauth_tokens_path.parent.mkdir(parents=True, exist_ok=True)
    return oauth_tokens_path


def prepare_tweets_db_file():
    tweets_db_path.parent.mkdir(parents=True, exist_ok=True)
    return tweets_db_path
