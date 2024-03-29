# Twema

Twema is a Twitter to e-mail gateway. It has the following features:

* Sends tweets from a home timeline
* Sends messages from a Twitter thread as a single message
* Shows pictures inline

# API price

Twitter now restricts access to the `home_timeline.json` API endpoint and requires one to pay $100/month for it.

Instead head over to a nearby Nitter instance and grab feeds for all Twitter accounts you'd like to read.

# Installation & configuration

* Install the tool (e.g. `pip install twema`)
* Configure local mail server to accept mail via `/usr/sbin/sendmail`
* Copy [example config](docs/config.toml.example) to `$HOME/.config/twema/config.toml`
* Fill in `mail.from` and `mail.to` values
* [Register an app](https://developer.twitter.com/en/docs/basics/apps/overview)
* Fill in `app.consumer_key` and `app.consumer_secret` values
* Make a sacrifice to Musk by upgrading to a tier that allows you to consume `home_timeline.json` API endpoint.
* Run `twema fetch` and follow instructions to authenticate to Twitter

# Usage

Fetch tweets:
```
$ twema fetch
```

Send e-mails:
```
$ twema send
```
