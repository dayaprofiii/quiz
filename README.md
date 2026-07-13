## Запуск

Запуск проекта выполняется через Docker Compose:

```bash
docker compose up --build
```

После запуска веб-приложение доступно по ссылке `http://127.0.0.1:3000`

## Тестовые аккаунты

```text
organizer@quiz.test / 123456
player@quiz.test / 123456
```

## Архитектура

```text
src/
  app/       состояние приложения, навигация, глобальные стили
  pages/     отдельные экраны интерфейса
  shared/    API-клиент, общие функции и UI-компоненты

backend/
  app/
    api/       HTTP-эндпоинты FastAPI
    core/      настройки и безопасность
    db/        подключение к PostgreSQL
    models/    SQLAlchemy-модели
    schemas/   Pydantic-схемы
    services/  бизнес-логика, комнаты, валидация
  alembic/     миграции базы данных

deploy/
  nginx.conf   production-прокси для frontend, API и WebSocket
```
