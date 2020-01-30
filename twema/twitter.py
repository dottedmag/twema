#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import json

import twitter

from . import config


def connect(consumer_key, consumer_secret):
    f = config.prepare_oauth_tokens_file()
    if not config.have_oauth_tokens():
        twitter.oauth_dance("Twema", consumer_key, consumer_secret, f)
    oauth_token, oauth_token_secret = twitter.oauth.read_token_file(f)
    oauth = twitter.oauth.OAuth(
        oauth_token, oauth_token_secret, consumer_key, consumer_secret
    )
    return twitter.api.Twitter(auth=oauth)


def get_tweets(twitter, **args):
    return twitter.statuses.home_timeline(
        count=200, tweet_mode="extended", **args
    )


def get_tweets_after(twitter, id):
    tweets = {}
    ts = get_tweets(twitter, since_id=id)
    while len(ts):
        for t in ts:
            tweets[t["id"]] = json.dumps(t)
        smallest_id = min(ts, key=lambda s: s["id"])["id"]
        ts = get_tweets(twitter, since_id=id, max_id=smallest_id - 1)
    return tweets
