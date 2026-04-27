<div align="center">

# 🎵 Muzika Roboto

### Powerful Telegram Music Bot built with **aiogram 3.x**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)]()
[![aiogram](https://img.shields.io/badge/aiogram-3.x-green.svg)]()
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)]()
[![AsyncIO](https://img.shields.io/badge/Async-First-purple.svg)]()
[![Tests](https://img.shields.io/badge/tests-pytest-success.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-clean-orange.svg)]()

Telegram bot for managing a personal music library, playlists, artists, albums, and scalable bot architecture.

**Can be used as:**

🎧 Production-ready music bot  
🧩 Template for Telegram bots  
📚 Example of Clean Architecture  
⚡ Async Python project reference

</div>

# ✨ Features

## 🎵 User Features

- Browse music library
- View artists and albums
- Create personal artists
- Build custom playlists
- Personal music collection
- Telegram-native interaction

## 👨‍💻 Developer Features

- aiogram 3.x
- Async SQLAlchemy ORM
- Repository Pattern
- Unit Of Work
- Clean Architecture
- Modular structure
- Easy testing
- Environment-based settings
- Ready for Railway / VPS / Docker

---

# 🧱 Tech Stack

| Layer | Technology |
|------|------------|
| Language | Python 3.8+ |
| Bot Framework | aiogram 3.x |
| ORM | SQLAlchemy 2.x |
| Validation | Pydantic |
| Config | pydantic-settings |
| Database | SQLite / PostgreSQL |
| Migrations | Alembic |
| Testing | Pytest |
| Async | asyncio |

---

# 📁 Project Structure

```text
muzika_roboto/
│── src/
│   ├── app/                # Bot application
│   ├── domain/             # Business logic
│   ├── infrastructure/     # DB / external services
│   └── core/               # Shared utilities
│
├── tests/
├── pyproject.toml
└── README.md
```


🚀 Quick Start
1️⃣ Clone repository

```bash
git clone https://github.com/razielSan/muzika_roboto.git
cd muzika_roboto
```


2️⃣ Create virtual environment

Linux / macOS

```python
python -m venv venv
source venv/bin/activate

```
Windows

```python
python -m venv venv
venv\Scripts\activate
```


3️⃣ Install dependencies

```bash
pip install -e .
```

or

```bash
pip install -r requirements.txt
```

⚙️ Configuration

Create file:

```bash
src/app/bot/.env
```

Example:

```.env
TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ADMINS_LIST=["123456789"]
```


🌍 Proxy Support

Webshare Proxy

```.env
WEBSHARE_LOGIN=login
WEBSHARE_PASSWORD=password
WEBSHARE_HOST=host
WEBSHARE_PORT=port
```

src/app/bot/settings.py

```python
class ProxySettings(BaseSettings):
    USE_WEBSHARE_PROXY: bool = True
```
Custom Proxy

```.env
OTHER_HOST=host
OTHER_PORT=port
```

src/app/bot/settings.py

```python
class ProxySettings(BaseSettings):
   USE_OTHER_PROXY: bool = True
```

▶️ Run Bot

```bash
bot
```

or manually:

```bash
PYTHONPATH=src python -m app.main
```


🧪 Testing

Run tests:

```bash
pytest
```

🏛 Architecture Principles

This project follows:

✅ Clean Architecture
✅ Separation of Concerns
✅ Dependency Injection style
✅ Repository Pattern
✅ Unit Of Work
✅ Async-first design
✅ Testable business logic


🗄 Database Support

Database	Status
SQLite	✅ Supported
PostgreSQL	✅ Recommended
Railway PostgreSQL	✅ Ready

☁️ Deployment

Supported platforms:

- Railway
- Render
- VPS
- Docker
- Linux Server

📌 Why This Project?

Most Telegram bots are simple scripts.

Muzika Roboto demonstrates how to build a scalable, maintainable, production-grade Telegram application with modern Python practices.


🤝 Contributing

Pull requests are welcome.

If you'd like to improve architecture, performance, or UX — feel free to open an issue.


📬 Contact

Telegram: @razielasus

⭐ Support Project

If this repository helped you:

Star the repo ⭐
Fork it 🍴
Share it 🚀

<div align="center">
🎵 Muzika Roboto — where Telegram meets music.
</div> ```