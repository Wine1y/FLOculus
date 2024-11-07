# FLOculus
  FLOculus is a simple Telegram-Bot created to search for new tasks on various Russian freelance platforms.
# Features
  - Flexible task filters (keyword, regex, by price e.t.c)
  - Multiple platforms supported
  - High extensibility (new platforms and filter types can be added easily)
# Supported Platforms
  - **fl.ru**
  - **freelance.ru**
  - **freelance.habr.com**
  - **kwork.ru**
# Configuration
  FLOculus can be configured using the following ENV-variables:
  - **BOT_TOKEN** - Telegram bot token
  - **LOG_LEVEL** - Python logging level, defaults to *WARNING*
  - **PARSING_INTERVAL_SECONDS** - Interval between parses in seconds, defaults to *90*
  - **PARSING_TASKS_LIMIT** - Max tasks per parsing, defaults to *15*
  - **DATABASE_URL** - Async SQLAlchemy database url, defaults to *sqlite+aiosqlite:///./db.sqlite*