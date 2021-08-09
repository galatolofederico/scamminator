# scamminator

**Blocking a scammer** is not enough. It is time to **fight back**.

Wouldn't be great if there was a tool that uses **Artificial Intelligence** to **reply** to a **scammer** on your behalf and **waste** their **time**?

This is exactly what ``scamminator`` does.

Scammers have a limited amount of time available and every second wasted trying to scam an Artificial Intelligence is a second not used to scam a real person.


## How does it works?

``scamminator`` has three components:

* Telegram Client
* Artificial Intelligence (DialoGPT)
* Telegram Bot

The **Telegram Bot** is used to control the **Telegram Client** and tell it which chats to auto-reply using the **Artificial Intelligence**

## Installation

Create a telegram bot using [@botfather](https://t.me/botfather). You will need the `API_TOKEN` later on.


Clone this repository

```
git clone https://github.com/galatolofederico/scamminator.git && cd scamminator
```

Copy the `.env` template

```
cp .env.template .env
```

Edit the `.env` file and set your `BOT_TOKEN` and your `BOT_PASSWORD`

```
vim .env
```

Build the containers

```
docker-compose build
```

Run the **Telegram Client** and log in using your phone number and OTP

```
docker-compose run tg
```

After logging in you can quit the client with `CTRL+D`. You are now ready to fight scammers.

## Usage

Run ``scamminator``

```
docker-compose up
```

You can now control ``scamminator`` using the bot you created.
