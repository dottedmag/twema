#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
import enum
import datetime
from collections import namedtuple
import json


def quote_url(tweet, url):
    if not tweet["is_quote_status"]:
        return False
    return tweet["quoted_status_permalink"]["expanded"] == url


def whole_tweet_is_rt(tweet):
    return "retweeted_status" in tweet and tweet["full_text"].startswith("RT @")


ParsedUser = namedtuple("ParsedUser", ["name", "atname", "url"])


class ChunkKind(enum.Enum):
    TEXT = 0
    LINK = 1
    HIDDEN = 2


Chunk = namedtuple("Chunk", ["begin", "end", "kind", "text", "link"])


class Text:
    def __init__(self, text):
        self.text = text
        self.chunks = [Chunk(0, len(text), ChunkKind.TEXT, None, None)]

    def __str__(self):
        return "<twema.Text " + str(self.text) + " " + str(self.chunks) + ">"

    def link(self, begin, end, text, link):
        self._replace_chunk(
            begin, end, Chunk(begin, end, ChunkKind.LINK, text, link)
        )

    def hide(self, begin, end):
        self._replace_chunk(
            begin, end, Chunk(begin, end, ChunkKind.HIDDEN, None, None)
        )

    def hide_all(self):
        self.chunks = [Chunk(0, len(self.text), ChunkKind.HIDDEN, None, None)]

    def _replace_chunk(self, begin, end, new_chunk):
        i, chunk = self._find_chunk(begin, end)
        out = []
        if chunk.begin < begin:
            out.append(Chunk(chunk.begin, begin, ChunkKind.TEXT, None, None))
        out.append(new_chunk)
        if end < chunk.end:
            out.append(Chunk(end, chunk.end, ChunkKind.TEXT, None, None))
        self.chunks = self.chunks[:i] + out + self.chunks[i + 1 :]

    def _find_chunk(self, begin, end):
        for i, chunk in enumerate(self.chunks):
            if chunk.begin <= begin and begin < chunk.end:
                if chunk.begin < end and end <= chunk.end:
                    return i, chunk
                else:
                    raise RuntimeError(
                        "[{},{}) overlaps with chunk [{}, {})".format(
                            begin, end, chunk.begin, chunk.end
                        )
                    )
        raise RuntimeError("can't find chunk for [{}, {})".format(begin, end))

    def plaintext(self):
        out = ""
        for chunk in self.chunks:
            if chunk.kind == ChunkKind.TEXT:
                out += self.text[chunk.begin : chunk.end]
        return out

    def html(self):
        out = ""
        for chunk in self.chunks:
            if chunk.kind == ChunkKind.TEXT:
                out += self.text[chunk.begin : chunk.end]
            elif chunk.kind == ChunkKind.LINK:
                out += '<a href="' + chunk.link + '">' + chunk.text + "</a>"
        return out


class MediaType(enum.Enum):
    PHOTO = 0
    VIDEO = 1
    GIF = 2


def media_type(m):
    if (
        m["type"] == "video"
        or "video_info" in m
        or "additional_media_info" in m
    ):
        return MediaType.VIDEO
    if m["type"] == "animated_gif":
        return MediaType.GIF
    if m["type"] == "photo":
        return MediaType.PHOTO
    raise SyntaxError("Don't know how to handle " + m["type"])


Media = namedtuple("Media", ["url", "type"])

ParsedTweet = namedtuple(
    "ParsedTweet",
    [
        "id",
        "url",
        "author",
        "text",
        "date",
        "quote",
        "retweet",
        "reply",
        "media",
    ],
)

Reply = namedtuple("Reply", ["id", "url"])


def parse_tweet(tweet):
    return _parse_tweet(json.loads(tweet))


def _parse_tweet(tweet):
    id = tweet["id_str"]
    author = ParsedUser(
        name=tweet["user"]["name"],
        atname="@" + tweet["user"]["screen_name"],
        url="https://twitter.com/" + tweet["user"]["screen_name"],
    )
    date = datetime.datetime.strptime(
        tweet["created_at"], "%a %b %d %H:%M:%S %z %Y"
    )
    text = Text(tweet["full_text"])

    entities = tweet.get("extended_entities")
    if entities is None:
        entities = tweet.get("entities")

    media = []
    for m in entities["media"] if entities and "media" in entities else []:
        mt = media_type(m)
        if mt == MediaType.VIDEO or mt == MediaType.GIF:
            media_url = m["expanded_url"]
        else:
            media_url = m["media_url_https"]
        media.append(Media(media_url, mt))

        assert len(m["indices"]) == 2
        medium_from = m["indices"][0]
        medium_to = m["indices"][1]
        text.hide(medium_from, medium_to)

    retweet = None
    if "retweeted_status" in tweet:
        retweet = _parse_tweet(tweet["retweeted_status"])
        media = []

    quote, quote_url = None, None
    if retweet is None and tweet["is_quote_status"]:
        if "quoted_status" in tweet:
            quote = _parse_tweet(tweet["quoted_status"])
            quote_url = tweet["quoted_status_permalink"]["expanded"]
        else:
            # No quote, treat as a link
            pass

    for url in tweet.get("entities", {}).get("urls", {}):
        if url["expanded_url"] == quote_url:
            text.hide(url["indices"][0], url["indices"][1])
        else:
            text.link(
                url["indices"][0],
                url["indices"][1],
                url["display_url"],
                url["expanded_url"],
            )

    for mention in tweet.get("entities").get("user_mentions"):
        text.link(
            mention["indices"][0],
            mention["indices"][1],
            "@" + mention["screen_name"],
            "https://twitter.com/" + mention["screen_name"],
        )

    if retweet is not None:
        text.hide_all()

    reply_id = tweet.get("in_reply_to_status_id_str")
    reply_author = tweet.get("in_reply_to_screen_name")

    reply = None
    if reply_id is not None:
        reply = Reply(
            reply_id,
            "https://twitter.com/" + reply_author + "/status/" + str(reply_id),
        )

    url = (
        "https://twitter.com/"
        + tweet["user"]["screen_name"]
        + "/status/"
        + str(id)
    )

    return ParsedTweet(
        id, url, author, text, date, quote, retweet, reply, media
    )


Thread = namedtuple("Thread", ["authors", "tweets"])


def collect_threads(tweets):
    threads = []
    tweets_to_threads = {}

    def find_thread(tweet):
        if tweet.id in tweets_to_threads:
            return tweets_to_threads[tweet.id]
        if tweet.retweet is not None and tweet.retweet.id in tweets_to_threads:
            return tweets_to_threads[tweet.retweet.id]
        if tweet.quote is not None and tweet.quote.id in tweets_to_threads:
            return tweets_to_threads[tweet.quote.id]
        if tweet.reply is not None and tweet.reply.id in tweets_to_threads:
            return tweets_to_threads[tweet.reply.id]

    for tweet in tweets:
        thread = find_thread(tweet)
        if thread is None:
            thread = []
            threads.append(thread)
        thread.append(tweet)
        tweets_to_threads[tweet.id] = thread
        if tweet.retweet is not None:
            tweets_to_threads[tweet.retweet.id] = thread
        if tweet.quote is not None:
            tweets_to_threads[tweet.quote.id] = thread
        if tweet.reply is not None:
            tweets_to_threads[tweet.reply.id] = thread

    out_threads = []
    for thread in threads:
        out_threads.append(
            Thread(
                list(set(map(lambda t: t.author, thread))),
                sorted(thread, key=lambda t: t.date),
            )
        )
    return out_threads


def have_tweet(tweet_id, thread):
    for thread_tweet in thread.tweets:
        if thread_tweet.id == tweet_id:
            return True
    return False


def tweet_ids(thread):
    ids = []
    for tweet in thread.tweets:
        ids.append(tweet.id)
    return ids


def parse_tweets(raw_tweets):
    tweets = []
    for raw_tweet in raw_tweets:
        tweets.append(parse_tweet(raw_tweet))
    return collect_threads(tweets)
