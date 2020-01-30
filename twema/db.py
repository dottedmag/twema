#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import sqlite3

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS tweets (
    id INTEGER PRIMARY KEY,
    content NOT NULL,
    sent NOT NULL DEFAULT 0
)
"""


def open():
    f = config.prepare_tweets_db_file()
    db = sqlite3.connect(f)
    db.execute(SCHEMA)
    db.commit()
    return db


def get_latest_saved_id(db):
    dt = db.execute("SELECT MAX(id) FROM tweets").fetchone()
    if dt:
        return dt[0]


def save_tweets(db, tweets):
    db.executemany(
        "INSERT INTO tweets (id, content) VALUES (?, ?)",
        [(k, v) for k, v in tweets.items()],
    )
    db.commit()


def get_tweet(db, id):
    row = db.execute("SELECT content FROM tweets WHERE id=?", [id]).fetchone()
    if row:
        return row[0]


def get_tweet_ids(db):
    for row in db.execute("SELECT id FROM tweets ORDER BY id").fetchall():
        yield row[0]


def get_unsent_tweets(db):
    for row in db.execute("SELECT content FROM tweets WHERE sent=0").fetchall():
        yield row[0]


def mark_tweets_as_sent(db, ids):
    db.executemany("UPDATE tweets SET sent=1 WHERE id=?", [(id,) for id in ids])
    db.commit()
