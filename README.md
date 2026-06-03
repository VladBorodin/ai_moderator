````markdown
# AI Moderator

AI Moderator - это FastAPI-приложение-прокладка для контекстной модерации сообщений.

Сервис получает JSON с коротким фрагментом переписки, отправляет последнее сообщение вместе с контекстом в AI provider и возвращает простой результат модерации.

Приложение не является форумом, чатом, игровой платформой или хранилищем пользовательских сообщений. Его задача - принять запрос от внешней системы, оценить контекст и вернуть результат.

## Для чего нужно приложение

AI Moderator нужен для случаев, когда внешняя система уже обнаружила потенциально проблемное сообщение и хочет проверить его контекст через ИИ.

Например:

Игровой чат
	↓
нашел подозрительное сообщение
	↓
отправил последние сообщения в AI Moderator
	↓
AI Moderator оценил последнее сообщение
	↓
вернул verdict администратору или внешней системе
````

Главная цель - не банить сообщение только по наличию грубого слова, а учитывать контекст.

Например:

```text
"Ну ты удачливый сукин сын!"
```

может быть дружеским подшучиванием.

А сообщение:

```text
"Ты тупой сукин сын, с тобой невозможно работать."
```

уже является прямым оскорблением.

## Принцип работы

```text
Внешняя система
	↓
POST /moderation/check
	↓
AI Moderator сохраняет входной request в журнал
	↓
берет активный AI provider из БД
	↓
берет активный prompt template из БД
	↓
отправляет переписку в AI provider
	↓
получает JSON-ответ
	↓
валидирует verdict, offense_level и description
	↓
сохраняет результат в PostgreSQL
	↓
возвращает ответ внешней системе
```

## Формат результата

AI Moderator возвращает:

```json
{
	"verdict": 0,
	"offense_level": 1,
	"description": "Фраза выглядит как дружеское подшучивание без явного намерения унизить."
}
```

Где:

```text
verdict:
0 - no_offensive
1 - offensive

offense_level:
0 - нарушения нет
1-3 - грубый или спорный тон без явного унижения
4-6 - оскорбительный или агрессивный контекст
7-8 - явное унижение, травля, угроза или враждебность
9-10 - пожелание смерти, жесткая угроза, дегуманизация, призыв к насилию
```

## Пример запроса

Endpoint:

```text
POST /moderation/check
```

Минимальный запрос:

```json
{
	"messages": [
		{
			"text": "Проверяемое сообщение"
		}
	]
}
```

Расширенный запрос:

```json
{
	"source_system": "game_chat",
	"chat_id": "match_123_chat",
	"user_id": "player_456",
	"user_name": "PlayerTwo",
	"external_message_id": "msg_789",
	"messages": [
		{
			"name": "PlayerOne",
			"text": "И мне выпал тот самый билет, и я победил!"
		},
		{
			"name": "PlayerTwo",
			"text": "Ну ты удачливый сукин сын!"
		}
	]
}
```

Пример ответа:

```json
{
	"chat_id": "match_123_chat",
	"user_id": "player_456",
	"result": {
		"verdict": 0,
		"offense_level": 1,
		"description": "Фраза выглядит как дружеское подшучивание без явного намерения унизить."
	}
}
```

## Административный UI

После запуска доступна административная панель:

```text
http://127.0.0.1:18080/
```

Разделы:

```text
Dashboard - главная страница
Проверка сообщения - ручная проверка JSON
Журнал проверок - история moderation checks
Настройки ИИ - настройка AI provider
Промты - настройка системного промта
Системные логи - просмотр app.log и error.log
```

UI предназначен для администратора сервиса. Обычным пользователям внешней системы он не нужен.

## Технологии

```text
Python
FastAPI
SQLAlchemy
PostgreSQL
Docker Compose
Jinja2
Vanilla JavaScript
CSS
```

## Требования для локального запуска

Нужно установить:

```text
Python 3.12+
Git
Docker Desktop
```

Также нужен AI provider, совместимый с OpenAI Chat Completions API, или локальный OpenAI-compatible endpoint.

Например:

```text
BotHub
OpenRouter
Ollama
LM Studio
vLLM
llama.cpp server
```

## Первый холодный запуск

### 1. Клонировать репозиторий

```bat
git clone https://github.com/VladBorodin/ai_moderator.git
cd ai_moderator
```

### 2. Создать виртуальное окружение

```bat
python -m venv .venv
```

### 3. Активировать виртуальное окружение

```bat
.venv\Scripts\activate
```

### 4. Установить зависимости

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Или использовать установочный файл:

```bat
install.bat
```

### 5. Создать `.env`

Скопировать пример:

```bat
copy .env.example .env
```

Пример `.env`:

```env
APP_HOST=127.0.0.1
APP_PORT=18080

AI_PROVIDER_TYPE=openai_compatible
AI_PROVIDER_URL=http://localhost:11434/v1/chat/completions
AI_MODEL_NAME=llama3.1
AI_API_KEY=
AI_TIMEOUT_SECONDS=60

DATABASE_URL=postgresql+psycopg://ai_moderator_user:ai_moderator_password@localhost:55432/ai_moderator
```

## Настройка PostgreSQL

По умолчанию проект использует PostgreSQL в Docker.

Файл:

```text
docker-compose.yml
```

Пример настроек:

```yaml
services:
  postgres:
    image: postgres:16
    container_name: ai_moderator_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ai_moderator
      POSTGRES_USER: ai_moderator_user
      POSTGRES_PASSWORD: ai_moderator_password
    ports:
      - "55432:5432"
    volumes:
      - ai_moderator_postgres_data:/var/lib/postgresql/data

volumes:
  ai_moderator_postgres_data:
```

Строка подключения в `.env` должна соответствовать этим настройкам:

```env
DATABASE_URL=postgresql+psycopg://ai_moderator_user:ai_moderator_password@localhost:55432/ai_moderator
```

Расшифровка:

```text
ai_moderator_user - пользователь PostgreSQL
ai_moderator_password - пароль
localhost - адрес БД
55432 - порт PostgreSQL на хосте
ai_moderator - имя базы данных
```

### Как изменить БД

Если нужно использовать свою PostgreSQL БД, измени только `DATABASE_URL` в `.env`.

Пример:

```env
DATABASE_URL=postgresql+psycopg://my_user:my_password@my_postgres_host:5432/my_database
```

Если используется Docker, также можно изменить значения в `docker-compose.yml`:

```yaml
POSTGRES_DB: my_database
POSTGRES_USER: my_user
POSTGRES_PASSWORD: my_password
ports:
  - "55432:5432"
```

После изменения `docker-compose.yml` и если база уже создавалась, для полного пересоздания dev-БД можно выполнить:

```bat
docker compose down -v
docker compose up -d
```

Внимание: `docker compose down -v` удаляет данные PostgreSQL volume.

## Запуск PostgreSQL

```bat
docker compose up -d
```

Проверить контейнер:

```bat
docker ps
```

Ожидаемый контейнер:

```text
ai_moderator_postgres
```

## Запуск приложения

```bat
start.cmd
```

После запуска:

```text
Admin UI: http://127.0.0.1:18080/
Swagger:  http://127.0.0.1:18080/docs
Health:   http://127.0.0.1:18080/health
```

При первом запуске приложение автоматически:

```text
создаст таблицы в PostgreSQL
создаст базовые системные настройки
создаст дефолтный prompt template
```

## Настройка AI provider

Открыть:

```text
http://127.0.0.1:18080/ai-provider-settings
```

Нужно указать:

```text
name - произвольное название
provider_type - тип провайдера, сейчас используется openai_compatible
provider_url - полный URL chat completions endpoint
model_name - имя модели
api_key - API ключ, если нужен
timeout_seconds - таймаут запроса
is_active - активен ли провайдер
```

### Пример для BotHub

```text
name = BotHub gpt-4o-mini
provider_type = openai_compatible
provider_url = https://openai.bothub.chat/v1/chat/completions
model_name = gpt-4o-mini
api_key = <твой API key>
timeout_seconds = 60
is_active = true
```

### Пример для Ollama

```text
name = Local Ollama
provider_type = openai_compatible
provider_url = http://localhost:11434/v1/chat/completions
model_name = llama3.1
api_key =
timeout_seconds = 60
is_active = true
```

### Важное замечание по AI provider

У разных AI provider могут отличаться:

```text
base URL
полный endpoint
формат имени модели
требования к API key
лимиты
доступность моделей
```

AI Moderator ожидает OpenAI-compatible endpoint формата:

```text
POST /chat/completions
```

и ответ формата:

```json
{
	"choices": [
		{
			"message": {
				"content": "{...}"
			}
		}
	]
}
```

Если провайдер возвращает другой формат, потребуется отдельная реализация provider adapter.

## Настройка промта

Открыть:

```text
http://127.0.0.1:18080/prompt-settings
```

Активный промт должен требовать строгий JSON:

```json
{
	"verdict": 0,
	"offense_level": 0,
	"description": "Краткий вывод модератора."
}
```

Важно: модель должна вернуть JSON без markdown.

Правильно:

```json
{
	"verdict": 1,
	"offense_level": 8,
	"description": "Последнее сообщение содержит агрессию и угрозу."
}
```

Неправильно:

````text
```json
{
	"verdict": 1
}
````

````

Приложение пытается извлечь JSON даже из markdown-блока, но лучше требовать чистый JSON в промте.

## Проверка работы

### 1. Проверить Health

```text
http://127.0.0.1:18080/health
````

Ожидаемый ответ:

```json
{
	"status": "ok"
}
```

### 2. Проверить Swagger

```text
http://127.0.0.1:18080/docs
```

### 3. Проверить AI provider

Открыть:

```text
http://127.0.0.1:18080/moderation-test
```

Пример дружеского контекста:

```json
[
	{
		"name": "Петр",
		"text": "И мне выпал тот самый билет, и я победил!"
	},
	{
		"name": "Сергей",
		"text": "Ну ты удачливый сукин сын!"
	}
]
```

Пример агрессивного контекста:

```json
[
	{
		"name": "Петр",
		"text": "Ты опять проиграл катку?"
	},
	{
		"name": "Сергей",
		"text": "Ты блять баран тупой, сука. Чтоб ты сдох и вся твоя семья тоже."
	}
]
```

## Журнал проверок

Открыть:

```text
http://127.0.0.1:18080/moderation-logs
```

В журнале сохраняются:

```text
source_system
chat_id
user_id
user_name
external_message_id
last_message_text
request_json
response_json
verdict
offense_level
description
processing_time_ms
error_text
created_on
```

## Системные логи

Открыть:

```text
http://127.0.0.1:18080/system-logs
```

Файлы логов:

```text
logs/app.log
logs/error.log
```

В UI можно:

```text
посмотреть последние строки app.log
посмотреть последние строки error.log
скачать app.log
скачать error.log
```

## Полезные Docker команды

Запустить БД:

```bat
docker compose up -d
```

Остановить БД:

```bat
docker compose down
```

Остановить БД и удалить данные:

```bat
docker compose down -v
```

Зайти в PostgreSQL:

```bat
docker exec -it ai_moderator_postgres psql -U ai_moderator_user -d ai_moderator
```

Показать таблицы:

```sql
\dt
```

## Частые проблемы

### Порт приложения занят

По умолчанию приложение использует:

```text
127.0.0.1:18080
```

Проверить порт:

```bat
netstat -ano | findstr :18080
```

Изменить порт можно в `.env`:

```env
APP_PORT=18081
```

### PostgreSQL не запускается

Проверить Docker:

```bat
docker ps
```

Запустить БД:

```bat
docker compose up -d
```

### Приложение не видит БД

Проверить `DATABASE_URL` в `.env`.

Также проверить, что порт в `DATABASE_URL` совпадает с портом в `docker-compose.yml`.

Например:

```text
docker-compose.yml: 55432:5432
.env: localhost:55432
```

### AI provider возвращает 404

Обычно это неправильный `provider_url`.

Проверь, нужен ли полный endpoint:

```text
https://.../v1/chat/completions
```

или только base URL.

В текущей версии AI Moderator ожидает именно полный `provider_url` до `chat/completions`.

### AI provider возвращает 401 или 403

Проверить:

```text
api_key
доступность модели
права аккаунта
формат Authorization header
```

AI Moderator отправляет ключ так:

```text
Authorization: Bearer <api_key>
```

### AI provider возвращает 429

Это rate limit.

Нужно:

```text
подождать
выбрать другую модель
проверить тариф/лимиты provider
```

### AI provider возвращает 503

Обычно модель временно недоступна.

Нужно:

```text
повторить позже
выбрать другую модель
проверить статус provider
```

### Модель возвращает невалидный JSON

Проверить активный промт.

Промт должен явно требовать:

```text
Верни строго JSON без markdown.
```

Также можно уменьшить `ai.max_tokens` или выбрать более стабильную instruct-модель.

## Что нельзя коммитить

В репозиторий не должны попадать:

```text
.env
.venv/
logs/
__pycache__/
локальные БД
секреты
API ключи
```

Для примера настроек используется:

```text
.env.example
```
