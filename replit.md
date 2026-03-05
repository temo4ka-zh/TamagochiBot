# TutorBot - Virtual Pet Telegram Bot

A Telegram bot implementing a virtual pet (Tamagotchi-style) game in Russian.

## Architecture

- **Language**: Python 3.12
- **Framework**: pyTelegramBotAPI (telebot)
- **Type**: Telegram bot (console process, no web frontend)

## Project Structure

```
TutorBot/
  TutorBot.py      - Main bot logic
  sticker.webp     - Sticker assets
  sticker1-4.webm  - Sticker assets
  tamagotchi.sql   - SQL schema (unused/reference)
```

## Features

- Create and manage virtual pets
- Feed and play with pets (affects food/mood stats)
- Pet leveling system (up to level 10)
- Pet revival if food or mood reaches 0
- Random developer jokes ("Разрядить обстановку")

## Configuration

- `TELEGRAM_BOT_TOKEN` - Telegram bot token (set as a Replit Secret)

## Running

The bot runs as a long-polling Telegram bot via the "Start application" workflow:
```
python TutorBot/TutorBot.py
```

## Dependencies

- pyTelegramBotAPI 4.x
