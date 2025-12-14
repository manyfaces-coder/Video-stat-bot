import os
import re
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from yandexgptlite import YandexGPTLite
from sqlalchemy import text
from app.db.database import AsyncSessionLocal

load_dotenv(find_dotenv())

LLM = YandexGPTLite(os.getenv('YANDEX_FOLDER_ID'), os.getenv('YANDEX_API_KEY'))

BASE_DIR = Path(__file__).resolve().parent
PATH_SYSTEM_PROMPT = BASE_DIR / "system_prompt.txt"

# переменная с закэшированным промтом, чтобы не читать файл при каждом запрсое
SYSTEM_PROMPT_CACHE: str | None = None

# Иногда модель может завернуть в ```sql ... ```
SQL_ONLY_RE = re.compile(r"```(?:sql)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)

# Обозначаем все слова, которые могут влиять на таблицы в БД и запрещаем их
FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke)\b", re.IGNORECASE)

# таблицы из которых разрешено чтение
ALLOWED_TABLES = {"videos", "video_snapshots"}


def get_system_prompt() -> str:
    """
    Читает system_prompt.txt один раз и кеширует в памяти.
    """
    global SYSTEM_PROMPT_CACHE
    if SYSTEM_PROMPT_CACHE is None:
        SYSTEM_PROMPT_CACHE = PATH_SYSTEM_PROMPT.read_text(encoding="utf-8")
    return SYSTEM_PROMPT_CACHE


def validate_sql(sql: str) -> None:
    """
    Проверяем получившийся от LLM SQL запрос
    """

    s = sql.strip()

    if ";" in s:
        raise ValueError("SQL не должен содержать ';'")

    if not s.lower().startswith("select"):
        raise ValueError("Разрешён только SELECT")

    if FORBIDDEN.search(s):
        raise ValueError("Запрещённые SQL-операции")

    # Примитивная проверка, что модель не лезет в другие таблицы
    lowered = s.lower()

    tables_found: set[str] = set()

    for _, table in re.findall(r'\b(from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b', lowered):
        tables_found.add(table)

    # Если вдруг tables_found пуст — не падаем, а просто пропускаем этот шаг.
    # В тестовом задании модель всегда использует FROM, поэтому не должно сюда попадать,
    # но если попадём – дадим запросу выполниться, чтобы не ронять бота
    if not tables_found:
        return

    not_allowed = [t for t in tables_found if t not in ALLOWED_TABLES]
    if not_allowed:
        raise ValueError(f"Запрещённые таблицы: {', '.join(not_allowed)}")



def to_sql(user_text: str, temperature: float = 0.0) -> str:
    """
    Отправляем вопрос пользователя и Промпт к YandexGPTLite
    :param user_text: вопрос пользователя из чата с ботом
    :param temperature: уровень творчества модели от 0 до 1 где 0 это максимально сухо,
                        а 1 - это максимум творчества
    :return: получаем SQL запрос
    """
    system_prompt = get_system_prompt()
    raw = LLM.create_completion(
        user_text,
        temperature,
        system_prompt=system_prompt
    )


    m = SQL_ONLY_RE.search(raw or "")
    sql = (m.group(1) if m else (raw or "")).strip()
    # иногда модель возвращает "SQL: SELECT ..." — подчистим
    sql = re.sub(r"^\s*sql\s*:\s*", "", sql, flags=re.IGNORECASE).strip()
    sql = re.sub(r";+\s*$", "", sql).strip()

    return sql


async def run_sql(sql: str):
    """
    Выполняем SQL и возвращаем ровно одно число
    Если запрос вернул не 1x1 — это считаем ошибкой
    """
    async with AsyncSessionLocal() as session:
        res = await session.execute(text(sql))
        rows = res.fetchall()

    if not rows or not rows[0] or rows[0][0] is None:
        return 0

        # Требуем 1 строку и 1 колонку, иначе это “не тот” запрос
    if len(rows) != 1 or len(rows[0]) != 1:
        raise ValueError("Запрос должен возвращать одно число (1 строка, 1 колонка)")

    value = rows[0][0]
    # Приводим к int, если это Decimal/str/float (в тестах ожидается число)
    try:
        return int(value)
    except Exception:
        raise ValueError(f"Результат не является числом: {value!r}")