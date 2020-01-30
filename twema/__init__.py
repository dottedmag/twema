#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import sys

from . import db, formatting, twitter, parse, mail


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


def send(config):
    d = db.open()

    raw_tweets = db.get_unsent_tweets(d)

    threads = parse.parse_tweets(raw_tweets)

    for thread in threads:
        msg = formatting.thread_email(config, thread)
        if mail.send(config, msg):
            db.mark_tweets_as_sent(d, parse.tweet_ids(thread))


# debugging commands


def get_raw_tweets(config, ids):
    d = db.open()

    if ids is None:
        ids = []
    elif ids == "all":
        ids = db.get_tweet_ids(d)
    else:
        ids = ids.split(",")

    return [db.get_tweet(d, id) for id in ids]


def render_email(config, ids):
    raw_tweets = get_raw_tweets(config, ids)

    threads = parse.parse_tweets(raw_tweets)

    for thread in threads:
        sys.stdout.buffer.write(formatting.thread_email(config, thread))


def render_html(config, ids):
    raw_tweets = get_raw_tweets(config, ids)

    threads = parse.parse_tweets(raw_tweets)

    for thread in threads:
        sys.stdout.write(formatting.thread_html(config, thread))


def list(config):
    d = db.open()
    for id in db.get_tweet_ids(d):
        print(id)


def print_raw(config, id):
    d = db.open()
    print(db.get_tweet(d, id))


def print_parsed_tweet(config, id):
    d = db.open()
    tweet = parse.parse_tweet(db.get_tweet(d, id))
    print(tweet)
    print(tweet.text)
