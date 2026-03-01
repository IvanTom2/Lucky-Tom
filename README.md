# Lucky-Tom

Open source система управления сетевыми игровыми автоматами для образовательных и развлекательных целей.

## Architecture

- **core/** — Core-сервис (монолит, Hexagonal Architecture): пользователи, баланс, регистрация слотов, игровые сессии
- **slot/** — Slot-сервис (шаблон, Hexagonal Architecture): игровая логика, версии, спины
- **analytics/** — Analytics-сервис: статистика спинов (ClickHouse)
- **proto/** — Общие .proto файлы для gRPC
- **docs/** — Проектная документация

## Tech Stack

- Python 3.13, FastAPI, SQLAlchemy async, gRPC
- PostgreSQL, Redis, RabbitMQ, ClickHouse
- Docker Compose for local development

## Quick Start

```bash
docker compose up -d
```

## License

MIT
