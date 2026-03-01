# Project Plan: Lucky-Tom

> Пошаговый план реализации для vibe-coding с AI-агентом.
> Каждый шаг — один модуль / один endpoint / одна интеграция.
> Каждый шаг проверяем изолированно перед переходом к следующему.

**Версия:** 0.1
**Дата:** 2026-02-28
**Автор:** Tomilov Ivan

---

## Обозначения

- 🟢 **Лёгкий** — конфиг, утилиты, простая логика, CRUD без бизнес-правил
- 🔴 **Тяжёлый** — бизнес-логика, интеграции, сложные инварианты

---

## ФАЗА 0: Инфраструктура и scaffolding

---

### Шаг 0.1 — Структура репозитория
🟢 **Лёгкий**

**Что делаем:** Создаём монорепозиторий с базовой структурой директорий для всех сервисов.

```
lucky-tom/
├── core/                  # Core-сервис
│   ├── src/
│   │   ├── domain/        # Бизнес-логика (hexagonal core)
│   │   ├── app/   # Use cases, ports
│   │   ├── adapters/      # REST, gRPC, DB, Cache адаптеры
│   ├── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── slot/                  # Шаблон Slot-сервиса
│   ├── src/
│   │   ├── domain/
│   │   ├── app/
│   │   ├── adapters/
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── analytics/             # Analytics-сервис
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── proto/                 # Общие .proto файлы
├── docker-compose.yml
└── README.md
```

**Зависимости:** —

**Затрагиваемые компоненты:** все сервисы, инфраструктура.

**Критерий готовности:**
```bash
ls -la lucky-tom/
# Все директории созданы
```

---

### Шаг 0.2 — pyproject.toml и зависимости
🟢 **Лёгкий**

**Что делаем:** Настраиваем `pyproject.toml` для каждого сервиса. Устанавливаем зависимости: FastAPI, SQLAlchemy async, alembic, grpcio, aio-pika, aioredis, structlog, pytest-asyncio.

**Зависимости:** 0.1

**Затрагиваемые компоненты:** все сервисы.

**Критерий готовности:**
```bash
cd core && pip install -e ".[dev]" && python -c "import fastapi; import sqlalchemy; print('OK')"
```

---

### Шаг 0.3 — Линтинг и форматирование
🟢 **Лёгкий**

**Что делаем:** Настраиваем ruff (линтер + форматтер) и mypy (type checking). Добавляем pre-commit хуки.

**Зависимости:** 0.2

**Затрагиваемые компоненты:** все сервисы.

**Критерий готовности:**
```bash
ruff check . && mypy src/
# Нет ошибок на пустом проекте
```

---

### Шаг 0.4 — Docker Compose: инфраструктура
🟢 **Лёгкий**

**Что делаем:** Пишем `docker-compose.yml` с инфраструктурными сервисами: PostgreSQL (две БД: core_db, slot_db), Redis, RabbitMQ, ClickHouse.

**Зависимости:** 0.1

**Затрагиваемые компоненты:** PostgreSQL, Redis, RabbitMQ, ClickHouse.

**Критерий готовности:**
```bash
docker compose up -d postgres redis rabbitmq clickhouse
docker compose ps
# Все сервисы в статусе healthy
```

---

### Шаг 0.5 — Пустой запускаемый Core-сервис
🟢 **Лёгкий**

**Что делаем:** Создаём минимальный FastAPI app с одним healthcheck endpoint. Настраиваем structlog. Dockerfile для Core.

**Зависимости:** 0.2, 0.3, 0.4

**Затрагиваемые компоненты:** Core-сервис.

**Критерий готовности:**
```bash
docker compose up core
curl http://localhost:8000/health
# {"status": "ok"}
```

---

### Шаг 0.6 — Пустой запускаемый Slot-сервис (шаблон)
🟢 **Лёгкий**

**Что делаем:** Создаём минимальный FastAPI app для Slot-сервиса с healthcheck. Dockerfile для Slot. Это будет эталонный шаблон для разработчиков.

**Зависимости:** 0.2, 0.3, 0.4

**Затрагиваемые компоненты:** Slot-сервис.

**Критерий готовности:**
```bash
docker compose up slot
curl http://localhost:8001/health
# {"status": "ok"}
```

---

### Шаг 0.7 — GitHub Actions: базовый CI pipeline
🟢 **Лёгкий**

**Что делаем:** Создаём `.github/workflows/ci.yml` — lint, type check, запуск тестов для каждого сервиса.

**Зависимости:** 0.3, 0.5, 0.6

**Затрагиваемые компоненты:** CI/CD.

**Критерий готовности:**
```
Push в main → GitHub Actions запускается → все шаги зелёные
```

---

## ФАЗА 1: Core-сервис — User & Balance

---

### Шаг 1.1 — SQLAlchemy: подключение к PostgreSQL (Core)
🟢 **Лёгкий**

**Что делаем:** Настраиваем async подключение SQLAlchemy к core_db. Базовый класс модели. Alembic инициализация.

**Зависимости:** 0.4, 0.5

**Затрагиваемые компоненты:** Core — PostgreSQL.

**Критерий готовности:**
```bash
cd core && alembic current
# Alembic подключился к БД, показывает текущую ревизию (None)
```

---

### Шаг 1.2 — Domain: модель User
🟢 **Лёгкий**

**Что делаем:** Создаём domain-модель `User` (dataclass/pydantic): username, password_hash, amount, is_active, created_at, deleted_at. Бизнес-правила: amount >= 0, soft delete.

**Зависимости:** 1.1

**Затрагиваемые компоненты:** Core — User & Balance домен.

**Критерий готовности:**
```bash
pytest tests/domain/test_user.py
# Тесты: нельзя создать user с amount < 0, soft delete работает
```

---

### Шаг 1.3 — ORM-модель и миграция: User
🟢 **Лёгкий**

**Что делаем:** SQLAlchemy ORM модель для User. Alembic миграция. Repository интерфейс (порт) и его PostgreSQL реализация (адаптер): create, get_by_id, get_by_username.

**Зависимости:** 1.2

**Затрагиваемые компоненты:** Core — User, PostgreSQL.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/adapters/test_user_repository.py
# CRUD тесты проходят
```

---

### Шаг 1.4 — Domain: модель Transaction
🟢 **Лёгкий**

**Что делаем:** Domain-модель `Transaction`: tid (UUID), user_id, balance_update (Decimal, положительный или отрицательный), comment. ORM модель, миграция, Repository.

**Зависимости:** 1.3

**Затрагиваемые компоненты:** Core — Transaction, PostgreSQL.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/adapters/test_transaction_repository.py
```

---

### Шаг 1.5 — Use case: регистрация пользователя (F-001)
🔴 **Тяжёлый**

**Что делаем:** Use case `RegisterUser`: хешируем пароль (bcrypt), создаём User с amount=0, генерируем сессионный токен (JWT). Порт для хеширования паролей и генерации токенов.

**Зависимости:** 1.3, 1.4

**Затрагиваемые компоненты:** Core — User & Balance, F-001.

**Критерий готовности:**
```bash
pytest tests/app/test_register_user.py
# Тесты: пользователь создан, баланс 0, токен выдан, дубликат username — ошибка
```

---

### Шаг 1.6 — REST endpoint: POST /auth/register
🟢 **Лёгкий**

**Что делаем:** FastAPI endpoint для регистрации. Pydantic схемы запроса/ответа. Dependency injection use case.

**Зависимости:** 1.5

**Затрагиваемые компоненты:** Core — REST API, F-001.

**Критерий готовности:**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: app/json" \
  -d '{"username": "player1", "password": "secret"}'
# {"token": "...", "user_id": "..."}
```

---

### Шаг 1.7 — Use case: изменение баланса (F-002, F-003)
🔴 **Тяжёлый**

**Что делаем:** Use case `UpdateBalance`: принимает user_id и balance_update (Decimal). Атомарно: проверяет что amount + balance_update >= 0, создаёт Transaction, обновляет User.amount. Всё в одной транзакции БД.

**Зависимости:** 1.4, 1.5

**Затрагиваемые компоненты:** Core — User & Balance, Transaction, F-002, F-003.

**Критерий готовности:**
```bash
pytest tests/app/test_update_balance.py
# Тесты: депозит увеличивает баланс, вывод уменьшает,
# вывод больше баланса — ошибка, баланс не уходит в минус
```

---

### Шаг 1.8 — REST endpoints: баланс (F-002, F-003)
🟢 **Лёгкий**

**Что делаем:** `POST /balance/deposit` и `POST /balance/withdraw`. Валидация: min 100, max 1_000_000 для депозита; min 100 для вывода. JWT аутентификация.

**Зависимости:** 1.6, 1.7

**Затрагиваемые компоненты:** Core — REST API, F-002, F-003.

**Критерий готовности:**
```bash
curl -X POST http://localhost:8000/balance/deposit \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"amount": 1000}'
# {"balance": 1000}

curl -X POST http://localhost:8000/balance/deposit \
  -d '{"amount": 50}'
# 422 — меньше минимума
```

---

### Шаг 1.9 — gRPC сервер: изменение баланса (входящий от Slot)
🔴 **Тяжёлый**

**Что делаем:** Определяем `.proto` для операций с балансом: `DebitBalance` (списать ставку) и `CreditBalance` (начислить выигрыш). Реализуем gRPC сервер в Core, переиспользуем use case из 1.7. Аутентификация по токену слота.

**Зависимости:** 1.7

**Затрагиваемые компоненты:** Core — gRPC сервер, User & Balance, proto/balance.proto.

**Критерий готовности:**
```bash
# Запустить grpc_server, вызвать через grpcurl:
grpcurl -plaintext -d '{"user_id": "...", "amount": "100"}' \
  localhost:50051 balance.BalanceService/DebitBalance
# {"success": true, "new_balance": "900"}
```

---

### Шаг 1.10 — Redis: подключение и сессии (Core)
🟢 **Лёгкий**

**Что делаем:** Настраиваем aioredis в Core. Порт SessionStore и его Redis реализация: create_session, get_session, delete_session с TTL.

**Зависимости:** 0.4, 0.5

**Затрагиваемые компоненты:** Core — Redis, Game Session.

**Критерий готовности:**
```bash
pytest tests/adapters/test_session_store.py
# Сессия создаётся, читается, истекает по TTL
```

---

## ФАЗА 2: Slot-сервис — создание и конфигурация слота

---

### Шаг 2.1 — SQLAlchemy: подключение к PostgreSQL (Slot)
🟢 **Лёгкий**

**Что делаем:** Аналогично 1.1 — async подключение к slot_db, Alembic инициализация.

**Зависимости:** 0.4, 0.6

**Затрагиваемые компоненты:** Slot — PostgreSQL.

**Критерий готовности:**
```bash
cd slot && alembic current
```

---

### Шаг 2.2 — Domain: модели версии слота
🔴 **Тяжёлый**

**Что делаем:** Domain-модели для Slot-сервиса: `Version` (name, description, deleted_at), `VersionConfig` (lines: list[int], bets: list[Decimal]), `SymbolVersion` (name), `SymbolVersionUI` (name, image, designation — уникальны в рамках версии), `SymbolVersionPayout` (table: dict[int, Decimal], валидация x(i) <= x(i+1)), `SymbolVersionConfig` (proba, multiplier, is_wild, is_scatter, bonus_game_only, extra).

**Зависимости:** 2.1

**Затрагиваемые компоненты:** Slot — Versions, VersionConfig, SymbolVersion и связанные, F-005.

**Критерий готовности:**
```bash
pytest tests/domain/test_version_models.py
# Тесты: payout table валидируется (x(i) <= x(i+1)),
# уникальность UI полей в рамках версии
```

---

### Шаг 2.3 — ORM-модели и миграции: версия слота
🟢 **Лёгкий**

**Что делаем:** ORM модели и миграции для всех сущностей из 2.2. Repository для Version: create, get_by_id, list.

**Зависимости:** 2.2

**Затрагиваемые компоненты:** Slot — PostgreSQL, все модели версии.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/adapters/test_version_repository.py
```

---

### Шаг 2.4 — Use case: создать версию слота (F-005)
🔴 **Тяжёлый**

**Что делаем:** Use case `CreateVersion`: принимает название, описание, список символов с их UI/Payout/Config, VersionConfig. Сохраняет все связанные сущности в одной транзакции. После создания — публикует событие в очередь (порт MessagePublisher, реализация заглушка пока).

**Зависимости:** 2.3

**Затрагиваемые компоненты:** Slot — F-005, все модели версии.

**Критерий готовности:**
```bash
pytest tests/app/test_create_version.py
# Версия создана со всеми символами, событие опубликовано
```

---

### Шаг 2.5 — Use case: скопировать версию слота (F-006)
🔴 **Тяжёлый**

**Что делаем:** Use case `CopyVersion`: принимает source_version_id и опциональный список переопределений (какие символы/UI/Payout скопировать, что переопределить). Создаёт новую версию на основе существующей.

**Зависимости:** 2.4

**Затрагиваемые компоненты:** Slot — F-006.

**Критерий готовности:**
```bash
pytest tests/app/test_copy_version.py
# Скопированная версия содержит все данные source,
# переопределённые поля — новые значения
```

---

### Шаг 2.6 — Domain: модель статистики версии
🔴 **Тяжёлый**

**Что делаем:** Domain-модель `VersionStatistics`: method, qiter, rtp, mean, std, var, wtb, hit, max. ORM модель, миграция. Бизнес-правило: берётся последняя статистика при валидации.

**Зависимости:** 2.3

**Затрагиваемые компоненты:** Slot — VersionStatistics, F-007.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/domain/test_statistics.py
```

---

### Шаг 2.7 — Use case: расчёт статистики версии (F-007)
🔴 **Тяжёлый**

**Что делаем:** Use case `CalculateStatistics`: запускается после создания версии. Симулирует N спинов используя конфигурацию версии (proba символов, payout table), рассчитывает RTP, mean, std, var, wtb, hit, max. Сохраняет результат в VersionStatistics.

**Зависимости:** 2.6

**Затрагиваемые компоненты:** Slot — VersionStatistics, F-007.

**Критерий готовности:**
```bash
pytest tests/app/test_calculate_statistics.py
# RTP рассчитан, значение разумное (0.8–1.2 для тестовой конфигурации)
# Статистика сохранена в БД
```

---

### Шаг 2.8 — Domain: модель Constraints (F-008)
🟢 **Лёгкий**

**Что делаем:** Domain-модель `Constraints`: min/max для rtp, mean, std, var, wtb, hit, max. ORM модель, миграция. Repository с UPSERT. Бизнес-правило: валидация статистики версии против ограничений.

**Зависимости:** 2.6

**Затрагиваемые компоненты:** Slot — Constraints, F-008.

**Критерий готовности:**
```bash
pytest tests/domain/test_constraints.py
# Версия с RTP вне диапазона — не проходит валидацию
```

---

### Шаг 2.9 — Use case: управление Constraints (F-008)
🟢 **Лёгкий**

**Что делаем:** Use case `UpsertConstraints`: создать или обновить ограничения слота. Use case `ValidateVersionAgainstConstraints`: проверить статистику версии против ограничений (использует последнюю статистику).

**Зависимости:** 2.8

**Затрагиваемые компоненты:** Slot — Constraints, F-008.

**Критерий готовности:**
```bash
pytest tests/app/test_constraints.py
# UPSERT работает, валидация отклоняет версию вне диапазона
```

---

### Шаг 2.10 — REST endpoints: управление версиями слота
🟢 **Лёгкий**

**Что делаем:** Endpoints для Slot-сервиса: `POST /versions` (создать версию, запускает расчёт статистики), `POST /versions/copy` (скопировать), `GET /versions/{id}` (получить версию), `PUT /constraints` (UPSERT ограничений).

**Зависимости:** 2.5, 2.7, 2.9

**Затрагиваемые компоненты:** Slot — REST API, F-005, F-006, F-007, F-008.

**Критерий готовности:**
```bash
curl -X POST http://localhost:8001/versions \
  -d '{"name": "v1", "symbols": [...], "config": {...}}'
# {"version_id": "...", "status": "calculating_stats"}

curl http://localhost:8001/versions/{id}
# {"version_id": "...", "statistics": {...}}
```

---

## ФАЗА 3: Slot-сервис — регистрация клиента

---

### Шаг 3.1 — .proto: регистрация клиента
🟢 **Лёгкий**

**Что делаем:** Определяем `proto/registration.proto`: сервис `RegistrationService`, метод `RegisterClient` (принимает name, balance_webhook, возвращает token).

**Зависимости:** 0.1

**Затрагиваемые компоненты:** proto/registration.proto, F-009.

**Критерий готовности:**
```bash
python -m grpc_tools.protoc --python_out=. --grpc_python_out=. proto/registration.proto
# Файлы сгенерированы без ошибок
```

---

### Шаг 3.2 — Domain: модель RegisteredClient
🟢 **Лёгкий**

**Что делаем:** Domain-модель `RegisteredClient`: name, balance_webhook, token (UUID). ORM модель, миграция, Repository: create, get_by_token.

**Зависимости:** 2.1, 3.1

**Затрагиваемые компоненты:** Slot — RegisteredClient, F-009.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/adapters/test_registered_client_repository.py
```

---

### Шаг 3.3 — Use case: регистрация клиента
🟢 **Лёгкий**

**Что делаем:** Use case `RegisterClient`: принимает name и balance_webhook, генерирует token, сохраняет RegisteredClient. Возвращает token.

**Зависимости:** 3.2

**Затрагиваемые компоненты:** Slot — RegisteredClient, F-009.

**Критерий готовности:**
```bash
pytest tests/app/test_register_client.py
```

---

### Шаг 3.4 — gRPC сервер: регистрация клиента (Slot)
🟢 **Лёгкий**

**Что делаем:** Реализуем gRPC сервер в Slot для `RegistrationService.RegisterClient`, переиспользуем use case из 3.3.

**Зависимости:** 3.3

**Затрагиваемые компоненты:** Slot — gRPC сервер, F-009.

**Критерий готовности:**
```bash
grpcurl -plaintext -d '{"name": "core", "balance_webhook": "localhost:50051"}' \
  localhost:50052 registration.RegistrationService/RegisterClient
# {"token": "..."}
```

---

## ФАЗА 4: Core-сервис — регистрация слота

---

### Шаг 4.1 — .proto: управление слотом (Core → Slot)
🟢 **Лёгкий**

**Что делаем:** Расширяем proto — `SlotManagementService`: `SetActiveVersion` (принимает version_id, возвращает ok). Используем registration.proto из шага 3.1.

**Зависимости:** 3.1

**Затрагиваемые компоненты:** proto/slot_management.proto, F-010.

**Критерий готовности:**
```bash
python -m grpc_tools.protoc ... proto/slot_management.proto
# Файлы сгенерированы
```

---

### Шаг 4.2 — Domain: модели RegisteredSlot, RegisteredSlotVersion
🟢 **Лёгкий**

**Что делаем:** Domain-модели и ORM для Core: `RegisteredSlot` (name, host, port, token, active), `RegisteredSlotVersion` (name, description), `RegisteredSlotActiveVersion` (UPSERT), `RegisteredSlotVersionSymbol`, `RegisteredSlotVersionStatistics`. Миграции.

**Зависимости:** 1.1

**Затрагиваемые компоненты:** Core — Slot Management, F-009.

**Критерий готовности:**
```bash
alembic upgrade head
pytest tests/adapters/test_slot_repository.py
```

---

### Шаг 4.3 — gRPC клиент: регистрация в Slot (Core)
🔴 **Тяжёлый**

**Что делаем:** gRPC клиент в Core для вызова `RegistrationService.RegisterClient` на Slot. Порт SlotRegistrationClient и его gRPC реализация. Таймаут — если Slot не отвечает, немедленная ошибка.

**Зависимости:** 3.4, 4.2

**Затрагиваемые компоненты:** Core — gRPC клиент, Slot Management, F-009.

**Критерий готовности:**
```bash
pytest tests/adapters/test_slot_grpc_client.py
# Core успешно регистрируется в Slot, получает token
# При недоступном Slot — ошибка с таймаутом
```

---

### Шаг 4.4 — Use case: зарегистрировать слот (F-009)
🔴 **Тяжёлый**

**Что делаем:** Use case `RegisterSlot`: принимает name, host, port. Отправляет gRPC запрос в Slot → получает token → сохраняет RegisteredSlot в Core. Если Slot недоступен — rollback, ошибка администратору.

**Зависимости:** 4.3

**Затрагиваемые компоненты:** Core — Slot Management, RegisteredSlot, F-009.

**Критерий готовности:**
```bash
pytest tests/app/test_register_slot.py
# Слот зарегистрирован в Core и Slot одновременно
# При недоступном Slot — ошибка, в Core ничего не сохранилось
```

---

### Шаг 4.5 — RabbitMQ: подключение и consumer (Core)
🔴 **Тяжёлый**

**Что делаем:** Настраиваем aio-pika в Core. Consumer подписывается на exchange версий слотов. Порт VersionEventHandler и его реализация: при получении события — сохраняет облегчённую копию в RegisteredSlotVersion + RegisteredSlotVersionSymbol + RegisteredSlotVersionStatistics.

**Зависимости:** 0.4, 4.2

**Затрагиваемые компоненты:** Core — RabbitMQ consumer, Slot Management, F-009.

**Критерий готовности:**
```bash
pytest tests/adapters/test_version_consumer.py
# Событие из очереди → данные сохранены в Core БД
# Повторное событие — идемпотентно (данные не дублируются)
```

---

### Шаг 4.6 — RabbitMQ: publisher (Slot)
🔴 **Тяжёлый**

**Что делаем:** Реализуем MessagePublisher (порт из шага 2.4) через aio-pika в Slot. При создании версии — публикует событие с данными версии и sequence_number. Durable exchange, persistent messages.

**Зависимости:** 0.4, 2.4

**Затрагиваемые компоненты:** Slot — RabbitMQ publisher, F-009.

**Критерий готовности:**
```bash
pytest tests/adapters/test_version_publisher.py
# Версия создана → сообщение появилось в RabbitMQ queue
# Core consumer получил сообщение → данные в Core БД
```

---

### Шаг 4.7 — REST endpoint: зарегистрировать слот (F-009)
🟢 **Лёгкий**

**Что делаем:** `POST /admin/slots/register` в Core. Аутентификация администратора.

**Зависимости:** 4.4

**Затрагиваемые компоненты:** Core — REST API, F-009.

**Критерий готовности:**
```bash
curl -X POST http://localhost:8000/admin/slots/register \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"name": "fruit-slot", "host": "localhost", "port": 8001}'
# {"slot_id": "...", "token": "..."}
```

---

## ФАЗА 5: Core-сервис — выбор и поиск слота

---

### Шаг 5.1 — Redis: кэш активной версии слота
🔴 **Тяжёлый**

**Что делаем:** Порт ActiveVersionCache и его Redis реализация: get_active_version(slot_id), set_active_version(slot_id, version_id), invalidate(slot_id). Стратегия: write-through при смене версии.

**Зависимости:** 1.10, 4.2

**Затрагиваемые компоненты:** Core — Redis, Slot Management.

**Критерий готовности:**
```bash
pytest tests/adapters/test_active_version_cache.py
# Set → Get возвращает значение
# Invalidate → Get возвращает None → fallback в БД
```

---

### Шаг 5.2 — gRPC клиент: смена активной версии (Core → Slot)
🔴 **Тяжёлый**

**Что делаем:** gRPC клиент в Core для `SlotManagementService.SetActiveVersion`. Порт SlotManagementClient.

**Зависимости:** 4.1, 4.3

**Затрагиваемые компоненты:** Core — gRPC клиент, F-010.

**Критерий готовности:**
```bash
pytest tests/adapters/test_slot_management_client.py
```

---

### Шаг 5.3 — gRPC сервер: SetActiveVersion (Slot)
🟢 **Лёгкий**

**Что делаем:** Реализуем `SlotManagementService.SetActiveVersion` в Slot. Проверяет: версия существует, статистика рассчитана, проходит Constraints. Обновляет активную версию внутри слота.

**Зависимости:** 4.1, 2.9

**Затрагиваемые компоненты:** Slot — gRPC сервер, F-010.

**Критерий готовности:**
```bash
grpcurl -d '{"version_id": "..."}' localhost:50052 \
  slot_management.SlotManagementService/SetActiveVersion
# {"success": true}
# Версия без статистики → ошибка
# Версия вне Constraints → ошибка
```

---

### Шаг 5.4 — Use case: сменить активную версию (F-010)
🔴 **Тяжёлый**

**Что делаем:** Use case `SetActiveVersion` в Core: отправляет gRPC запрос в Slot → при успехе обновляет RegisteredSlotActiveVersion в БД → инвалидирует кэш → записывает новую версию в кэш.

**Зависимости:** 5.1, 5.2, 5.3

**Затрагиваемые компоненты:** Core — Slot Management, F-010.

**Критерий готовности:**
```bash
pytest tests/app/test_set_active_version.py
# Версия сменена: БД обновлена, кэш обновлён
```

---

### Шаг 5.5 — Use case + endpoint: поиск слотов (F-011)
🟢 **Лёгкий**

**Что делаем:** Use case `ListSlots`: возвращает активные слоты с их текущей версией (из кэша или БД). REST endpoint `GET /slots`.

**Зависимости:** 5.1, 4.2

**Затрагиваемые компоненты:** Core — Slot Management, F-011.

**Критерий готовности:**
```bash
curl http://localhost:8000/slots
# [{"slot_id": "...", "name": "fruit-slot", "active_version": {...}}]
```

---

### Шаг 5.6 — REST endpoints: управление версиями и слотами (F-010)
🟢 **Лёгкий**

**Что делаем:** `PUT /admin/slots/{slot_id}/active-version` — сменить активную версию. `PUT /admin/slots/{slot_id}/deactivate` и `PUT /admin/slots/{slot_id}/activate` — остановить/включить слот (F-014, F-015).

**Зависимости:** 5.4

**Затрагиваемые компоненты:** Core — REST API, F-010, F-014, F-015.

**Критерий готовности:**
```bash
curl -X PUT http://localhost:8000/admin/slots/{id}/active-version \
  -d '{"version_id": "..."}'
# {"success": true}
```

---

## ФАЗА 6: Game Session — подключение к слоту

---

### Шаг 6.1 — Domain: модель GameSession
🟢 **Лёгкий**

**Что делаем:** Domain-модель `GameSession`: session_id, user_id, slot_id, status (active/expired), created_at. Бизнес-правило: одна активная сессия на игрока.

**Зависимости:** 1.10

**Затрагиваемые компоненты:** Core — Game Session, Redis.

**Критерий готовности:**
```bash
pytest tests/domain/test_game_session.py
```

---

### Шаг 6.2 — Use case: подключиться к слоту (F-012)
🔴 **Тяжёлый**

**Что делаем:** Use case `ConnectToSlot`: проверяет что у игрока нет активной сессии (Redis), проверяет что слот активен, создаёт GameSession в Redis с TTL, возвращает адрес Slot-сервиса для WebSocket подключения.

**Зависимости:** 6.1, 5.1

**Затрагиваемые компоненты:** Core — Game Session, Redis, F-012.

**Критерий готовности:**
```bash
pytest tests/app/test_connect_to_slot.py
# Сессия создана, возвращён адрес слота
# Попытка второй сессии — ошибка
# Слот неактивен — ошибка
```

---

### Шаг 6.3 — REST endpoint: подключиться к слоту (F-012)
🟢 **Лёгкий**

**Что делаем:** `POST /slots/{slot_id}/connect` — создаёт сессию, возвращает WebSocket URL Slot-сервиса.

**Зависимости:** 6.2

**Затрагиваемые компоненты:** Core — REST API, F-012.

**Критерий готовности:**
```bash
curl -X POST http://localhost:8000/slots/{slot_id}/connect \
  -H "Authorization: Bearer $TOKEN"
# {"ws_url": "ws://localhost:8001/game", "session_token": "..."}
```

---

## ФАЗА 7: Slot-сервис — обработка спинов

---

### Шаг 7.1 — Domain: геймблинг-алгоритм (базовый)
🔴 **Тяжёлый**

**Что делаем:** Domain-сервис `SpinEngine`: принимает VersionConfig + список символов с их SymbolVersionConfig (proba, is_wild, is_scatter). Генерирует результат спина: набор символов на барабанах, список выигрышных линий, итоговый выигрыш (Decimal) с учётом payout table и multiplier.

**Зависимости:** 2.2

**Затрагиваемые компоненты:** Slot — игровая логика, F-013.

**Критерий готовности:**
```bash
pytest tests/domain/test_spin_engine.py
# Спин возвращает валидный результат
# RTP симуляции близок к теоретическому (±5%)
# Wild и Scatter символы обрабатываются корректно
```

---

### Шаг 7.2 — Domain: идемпотентность спина
🔴 **Тяжёлый**

**Что делаем:** Порт SpinStateStore и его Redis реализация: set_spin_in_progress(session_id), clear_spin(session_id), is_spin_in_progress(session_id). Атомарная операция через Redis SET NX.

**Зависимости:** 7.1

**Затрагиваемые компоненты:** Slot — Redis, идемпотентность, F-013.

**Критерий готовности:**
```bash
pytest tests/adapters/test_spin_state.py
# Параллельные вызовы set_spin_in_progress — только один возвращает true
```

---

### Шаг 7.3 — gRPC клиент с Circuit Breaker (Slot → Core)
🔴 **Тяжёлый**

**Что делаем:** gRPC клиент в Slot для вызова `BalanceService.DebitBalance` и `BalanceService.CreditBalance` в Core. Circuit Breaker: N ретраев → открытие при N неудачах → автоматическое закрытие при восстановлении.

**Зависимости:** 1.9

**Затрагиваемые компоненты:** Slot — gRPC клиент, Circuit Breaker, F-013.

**Критерий готовности:**
```bash
pytest tests/adapters/test_balance_grpc_client.py
# Успешный вызов — баланс изменён
# Core недоступен N раз → Circuit Breaker открывается → быстрый отказ
```

---

### Шаг 7.4 — Use case: сделать спин (F-013)
🔴 **Тяжёлый**

**Что делаем:** Use case `ProcessSpin`: 1) проверить идемпотентность (SpinStateStore), 2) gRPC DebitBalance в Core, 3) SpinEngine.spin(), 4) gRPC CreditBalance в Core, 5) сохранить в VersionSpinStatistics (ClickHouse через RabbitMQ), 6) очистить SpinStateStore, 7) вернуть результат.

**Зависимости:** 7.1, 7.2, 7.3

**Затрагиваемые компоненты:** Slot — F-013, SpinEngine, VersionSpinStatistics.

**Критерий готовности:**
```bash
pytest tests/app/test_process_spin.py
# Полный flow: баланс списан, выигрыш начислен, результат возвращён
# Параллельный спин — отказ
# Core недоступен — Circuit Breaker, ошибка игроку
```

---

### Шаг 7.5 — WebSocket endpoint: игровая сессия (F-012, F-013)
🔴 **Тяжёлый**

**Что делаем:** WebSocket endpoint `WS /game` в Slot. Аутентификация по session_token (из шага 6.3). Обработка сообщений: `{"action": "spin", "bet": 100, "lines": 5}` → ProcessSpin → возвращает результат.

**Зависимости:** 7.4, 6.3

**Затрагиваемые компоненты:** Slot — WebSocket, F-012, F-013.

**Критерий готовности:**
```python
# Тест через websockets:
async with websockets.connect("ws://localhost:8001/game?token=...") as ws:
    await ws.send('{"action": "spin", "bet": 100, "lines": 5}')
    result = await ws.recv()
    assert "win" in json.loads(result)
```

---

### Шаг 7.6 — Analytics: ClickHouse подключение и схема
🟢 **Лёгкий**

**Что делаем:** Analytics-сервис. Подключение к ClickHouse. Создаём таблицу `spin_statistics` (slot_id, version_id, user_id, bet, win, bonus_game, created_at). MergeTree движок.

**Зависимости:** 0.4, 4.6

**Затрагиваемые компоненты:** Analytics — ClickHouse, VersionSpinStatistics.

**Критерий готовности:**
```bash
clickhouse-client -q "SHOW TABLES" # spin_statistics есть
pytest tests/adapters/test_clickhouse.py
```

---

### Шаг 7.7 — Analytics: RabbitMQ consumer → ClickHouse
🔴 **Тяжёлый**

**Что делаем:** RabbitMQ consumer в Analytics-сервисе: подписывается на события спинов от Slot-сервисов, пишет batch-вставки в ClickHouse.

**Зависимости:** 7.6, 4.6

**Затрагиваемые компоненты:** Analytics — RabbitMQ consumer, ClickHouse, VersionSpinStatistics.

**Критерий готовности:**
```bash
# Сделать спин → проверить через clickhouse-client:
clickhouse-client -q "SELECT * FROM spin_statistics ORDER BY created_at DESC LIMIT 1"
# Запись появилась
```

---

## ФАЗА 8: Остановка и активация слота

---

### Шаг 8.1 — Use case: остановить / активировать слот (F-014, F-015)
🟢 **Лёгкий**

**Что делаем:** Use case `DeactivateSlot` / `ActivateSlot` в Core: меняет флаг `active` у RegisteredSlot. При деактивации — инвалидирует кэш слота. `ConnectToSlot` проверяет флаг active (уже есть в шаге 6.2).

**Зависимости:** 6.2, 5.1

**Затрагиваемые компоненты:** Core — Slot Management, RegisteredSlot, F-014, F-015.

**Критерий готовности:**
```bash
pytest tests/app/test_deactivate_slot.py
# Слот деактивирован → ConnectToSlot возвращает ошибку
# Слот активирован → ConnectToSlot работает
```

---

## ФАЗА 9: Интеграционное тестирование

---

### Шаг 9.1 — E2E тест: полный flow игрока
🔴 **Тяжёлый**

**Что делаем:** Интеграционный тест через docker-compose: регистрация → депозит → поиск слотов → подключение → спин → проверка баланса → отключение.

**Зависимости:** все предыдущие шаги.

**Затрагиваемые компоненты:** все сервисы.

**Критерий готовности:**
```bash
pytest tests/e2e/test_player_flow.py
# Полный сценарий проходит, баланс корректен
```

---

### Шаг 9.2 — E2E тест: полный flow администратора
🔴 **Тяжёлый**

**Что делаем:** Интеграционный тест: регистрация слота → создание версии → расчёт статистики → смена активной версии → смена во время активной игры → деактивация слота.

**Зависимости:** 9.1

**Затрагиваемые компоненты:** все сервисы.

**Критерий готовности:**
```bash
pytest tests/e2e/test_admin_flow.py
# Все сценарии проходят
```

---

## Сводная таблица шагов

| Шаг | Название | Сложность | Зависимости |
|-----|----------|-----------|-------------|
| 0.1 | Структура репозитория | 🟢 | — |
| 0.2 | pyproject.toml и зависимости | 🟢 | 0.1 |
| 0.3 | Линтинг и форматирование | 🟢 | 0.2 |
| 0.4 | Docker Compose: инфраструктура | 🟢 | 0.1 |
| 0.5 | Пустой Core-сервис | 🟢 | 0.2, 0.3, 0.4 |
| 0.6 | Пустой Slot-сервис | 🟢 | 0.2, 0.3, 0.4 |
| 0.7 | GitHub Actions CI | 🟢 | 0.3, 0.5, 0.6 |
| 1.1 | SQLAlchemy Core | 🟢 | 0.4, 0.5 |
| 1.2 | Domain: User | 🟢 | 1.1 |
| 1.3 | ORM + миграция: User | 🟢 | 1.2 |
| 1.4 | Domain: Transaction | 🟢 | 1.3 |
| 1.5 | Use case: регистрация | 🔴 | 1.3, 1.4 |
| 1.6 | REST: POST /auth/register | 🟢 | 1.5 |
| 1.7 | Use case: изменение баланса | 🔴 | 1.4, 1.5 |
| 1.8 | REST: баланс | 🟢 | 1.6, 1.7 |
| 1.9 | gRPC сервер: баланс (Core) | 🔴 | 1.7 |
| 1.10 | Redis: сессии (Core) | 🟢 | 0.4, 0.5 |
| 2.1 | SQLAlchemy Slot | 🟢 | 0.4, 0.6 |
| 2.2 | Domain: модели версии | 🔴 | 2.1 |
| 2.3 | ORM + миграции: версия | 🟢 | 2.2 |
| 2.4 | Use case: создать версию | 🔴 | 2.3 |
| 2.5 | Use case: скопировать версию | 🔴 | 2.4 |
| 2.6 | Domain: статистика версии | 🔴 | 2.3 |
| 2.7 | Use case: расчёт статистики | 🔴 | 2.6 |
| 2.8 | Domain: Constraints | 🟢 | 2.6 |
| 2.9 | Use case: Constraints | 🟢 | 2.8 |
| 2.10 | REST: версии слота | 🟢 | 2.5, 2.7, 2.9 |
| 3.1 | .proto: регистрация клиента | 🟢 | 0.1 |
| 3.2 | Domain: RegisteredClient | 🟢 | 2.1, 3.1 |
| 3.3 | Use case: регистрация клиента | 🟢 | 3.2 |
| 3.4 | gRPC сервер: регистрация (Slot) | 🟢 | 3.3 |
| 4.1 | .proto: управление слотом | 🟢 | 3.1 |
| 4.2 | Domain: RegisteredSlot и версии | 🟢 | 1.1 |
| 4.3 | gRPC клиент: регистрация (Core) | 🔴 | 3.4, 4.2 |
| 4.4 | Use case: зарегистрировать слот | 🔴 | 4.3 |
| 4.5 | RabbitMQ consumer (Core) | 🔴 | 0.4, 4.2 |
| 4.6 | RabbitMQ publisher (Slot) | 🔴 | 0.4, 2.4 |
| 4.7 | REST: зарегистрировать слот | 🟢 | 4.4 |
| 5.1 | Redis: кэш активной версии | 🔴 | 1.10, 4.2 |
| 5.2 | gRPC клиент: смена версии (Core) | 🔴 | 4.1, 4.3 |
| 5.3 | gRPC сервер: SetActiveVersion (Slot) | 🟢 | 4.1, 2.9 |
| 5.4 | Use case: сменить активную версию | 🔴 | 5.1, 5.2, 5.3 |
| 5.5 | Use case + REST: поиск слотов | 🟢 | 5.1, 4.2 |
| 5.6 | REST: управление слотами | 🟢 | 5.4 |
| 6.1 | Domain: GameSession | 🟢 | 1.10 |
| 6.2 | Use case: подключиться к слоту | 🔴 | 6.1, 5.1 |
| 6.3 | REST: подключиться к слоту | 🟢 | 6.2 |
| 7.1 | Domain: SpinEngine | 🔴 | 2.2 |
| 7.2 | Domain: идемпотентность спина | 🔴 | 7.1 |
| 7.3 | gRPC клиент + Circuit Breaker (Slot) | 🔴 | 1.9 |
| 7.4 | Use case: сделать спин | 🔴 | 7.1, 7.2, 7.3 |
| 7.5 | WebSocket: игровая сессия | 🔴 | 7.4, 6.3 |
| 7.6 | Analytics: ClickHouse схема | 🟢 | 0.4, 4.6 |
| 7.7 | Analytics: consumer → ClickHouse | 🔴 | 7.6, 4.6 |
| 8.1 | Use case: стоп/старт слота | 🟢 | 6.2, 5.1 |
| 9.1 | E2E: flow игрока | 🔴 | все |
| 9.2 | E2E: flow администратора | 🔴 | 9.1 |

---

## Changelog

| Дата | Версия | Что изменилось |
|------|--------|----------------|
| 2026-02-28 | 0.1 | Первая версия |
