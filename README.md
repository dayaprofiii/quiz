## Запуск

Проект запускается одной командой через Docker Compose:

```bash
docker compose up --build
```

После запуска приложение доступно по адресу:

```text
http://127.0.0.1:3000
```

## Архитектура

```text
frontend/
  src/
    app/       состояние приложения, навигация, глобальные стили
    pages/     отдельные экраны интерфейса
    shared/    API-клиент, общие функции и UI-компоненты
  public/      статические файлы
  scripts/     сборка клиентского приложения
  Dockerfile   сборка frontend
  nginx.conf   раздача frontend, проксирование API и WebSocket

backend/
  app/
    api/       HTTP-эндпоинты FastAPI
    core/      настройки и безопасность
    db/        подключение к PostgreSQL
    models/    SQLAlchemy-модели
    schemas/   Pydantic-схемы
    services/  бизнес-логика, комнаты, валидация
  alembic/     миграции базы данных
  Dockerfile   сборка backend

docker-compose.yml
  web, api и PostgreSQL в единой конфигурации
```
