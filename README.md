# VideoStatBot

Telegram-бот для аналитики по видео на основе данных из PostgreSQL.
Бот принимает вопросы на русском языке и возвращает числовой результат, рассчитанный по данным.

## Стек

* Python 3.12
* PostgreSQL 15
* SQLAlchemy
* aiogram 3
* Docker / Docker Compose
* YandexGPT (LLM)

---

## Структура проекта

```
app/
├── bot/
│   └── main.py            # запуск Telegram-бота
├── api/
│   └── request_handler.py # генерация SQL, валидация и выполнение запросов
├── db/
│   ├── models.py          # модели БД
│   ├── database.py        # подключение к PostgreSQL
│   └── load_data.py       # импорт данных из JSON
├── system_prompt.txt      # описание схемы БД для LLM
/data
├── videos.json
.env
docker-compose.yml
Dockerfile
requirements.txt
```

---

## Подготовка

1. Создать файл `.env`:

```env
BOT_TOKEN=...

POSTGRES_DB=videostat
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

YANDEX_FOLDER_ID=...
YANDEX_API_KEY=...
```

2. (Опционально) если нужен доступ к БД с хоста — оставить проброс порта `5432`.

---

## Запуск проекта

```bash
docker compose build
docker compose up -d
```

PostgreSQL и бот будут запущены в отдельных контейнерах.

---

## Загрузка данных в БД

Импорт данных выполняется отдельным скриптом:

```md
```bash
docker compose exec bot python -m app.db.load_data
```

```md
Скрипт запускается как Python-модуль (`-m`), чтобы корректно работали импорты внутри пакета `app`.
```
 
Скрипт:

* читает большой JSON-файл потоково (`ijson`),
* загружает данные в таблицы `videos` и `video_snapshots`,
* безопасен к повторному запуску (используется `ON CONFLICT DO NOTHING`).

---

## Использование бота

После запуска напишите боту в Telegram.

Примеры вопросов:

* `Сколько всего видео есть в системе?`
* `Сколько разных видео получали новые просмотры 27 ноября 2025?`
* `На сколько просмотров в сумме выросли все видео 28 ноября 2025?`

Бот всегда возвращает **одно числовое значение**, как требуется в тестовом задании.

---

## Как работает обработка запроса

1. Пользователь задаёт вопрос на русском языке.
2. Вопрос передаётся в LLM (YandexGPT) вместе с описанием схемы БД.
3. LLM генерирует SQL-запрос.
4. SQL проходит валидацию:

   * разрешён только `SELECT`,
   * только таблицы `videos` и `video_snapshots`,
   * запрещены DDL/DML операции.
5. SQL выполняется в PostgreSQL.
6. Результат (одно число) возвращается пользователю.

---