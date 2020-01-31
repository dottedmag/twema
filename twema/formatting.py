#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
from email.message import EmailMessage

from jinja2 import Environment, select_autoescape, PackageLoader

from . import parse


def subjectify(s):
    return " ".join(s.split())


def format_subject(thread):
    subject = thread.authors[0].atname
    if len(thread.authors) > 1:
        subject += " (+" + str(len(thread.authors) - 1) + ")"

    t = subjectify(thread.tweets[0].text.plaintext())
    if t == "":
        if thread.tweets[0].retweet is not None:
            t = ": RT " + subjectify(thread.tweets[0].retweet.text.plaintext())
        else:
            subject += ": <no text>"
    else:
        subject += ": " + t

    if len(thread.tweets) > 1:
        subject += " (+" + str(len(thread.tweets) - 1) + ")"

    return subject


jenv = Environment(
    loader=PackageLoader("twema", "templates"),
    autoescape=select_autoescape(["html"]),
)

thread_template = jenv.get_template("thread.jinja")


def thread_html(config, thread):
    return thread_template.render(
        thread=thread,
        is_pic=lambda media: media.type == parse.MediaType.PHOTO,
        have_tweet=parse.have_tweet,
    )


def thread_email(config, thread):
    msg = EmailMessage()
    msg["Subject"] = format_subject(thread)
    msg["From"] = config["mail"]["from"]
    msg["To"] = config["mail"]["to"]

    msg.set_content("See HTML version")
    msg.add_alternative(thread_html(config, thread), subtype="html")

    return bytes(msg)
