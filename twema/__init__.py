#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import sys

from . import db, formatting, twitter, parse, mail


def render(config, id):
    d = db.open()

    raw_tweets = []

    if id == "all":
        for id in db.get_tweet_ids(d):
            raw_tweets.append(db.get_tweet(d, id))
    else:
        raw_tweets.append(db.get_tweet(d, id))

    threads = parse.parse_tweets(raw_tweets)

    for thread in threads:
        msg = formatting.thread_html(config, thread)
        sys.stdout.buffer.write(msg)


def fetch(config):
    d = db.open()
    t = twitter.connect(
        config["app"]["consumer_key"], config["app"]["consumer_secret"],
    )

    latest_saved_id = db.get_latest_saved_id(d)
    if latest_saved_id:
        tweets = twitter.get_tweets_after(t, latest_saved_id)
    else:
        tweets = twitter.get_tweets(t)

    db.save_tweets(d, tweets)


def list(config):
    d = db.open()
    for id in db.get_tweet_ids(d):
        print(id)


def cmd_print(config, id):
    d = db.open()
    print(db.get_tweet(d, id))


def send(config):
    d = db.open()

    raw_tweets = db.get_unsent_tweets(d)

    threads = parse.parse_tweets(raw_tweets)

    for thread in threads:
        msg = formatting.thread_html(config, thread)
        if mail.send(config, msg):
            db.mark_tweets_as_sent(d, parse.tweet_ids(thread))
