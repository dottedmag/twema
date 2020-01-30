# Twema

Twema is a Twitter to e-mail gateway. It has the following features:

* Sends tweets from a home timeline
* Sends messages from a Twitter thread as a single message
* Shows pictures inline

# Installation & configuration

* Install the tool (e.g. `pip install twema`)
* Configure local mail server to accept mail via `/usr/sbin/sendmail`
* Copy [example config](docs/config.toml.example) to `$HOME/.config/twema/config.toml`
* Fill in `mail.from` and `mail.to` values
* [Register an app](https://developer.twitter.com/en/docs/basics/apps/overview)
* Fill in `app.consumer_key` and `app.consumer_secret` values
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
