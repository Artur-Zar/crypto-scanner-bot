# main.py
import sqlite3
import asyncio
import os
import sys

# Магия для PyCharm: добавляем текущую директорию в пути поиска
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from parsers import protocol_parser


def setup_db():
    """Создает базу и таблицу для вакансий"""
    conn = sqlite3.connect(config.DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            link TEXT UNIQUE,
            location TEXT,
            source TEXT,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn


async def run_collectors():
    # Инициализируем БД
    conn = setup_db()
    cursor = conn.cursor()

    print("🚀 Начинаю глобальный поиск вакансий (США, Европа, Канада, Грузия)...")

    # Вызываем парсер
    try:
        found_jobs = await protocol_parser.parse_protocol(config.KEYWORDS, config.LOCATIONS)
    except Exception as e:
        print(f"❌ Ошибка в работе системы: {e}")
        return

    # Сохраняем без дубликатов
    new_count = 0
    for job in found_jobs:
        try:
            cursor.execute(
                "INSERT INTO jobs (title, link, location, source) VALUES (?, ?, ?, ?)",
                (job['title'], job['link'], job['location'], 'theprotocol')
            )
            print(f"✅ Сохранено: {job['title']} [{job['location']}]")
            new_count += 1
        except sqlite3.IntegrityError:
            # Ссылка уже есть в базе, просто идем дальше
            continue

    conn.commit()
    conn.close()
    print(f"\n🏁 Поиск завершен. Найдено новых вакансий: {new_count}")


if __name__ == "__main__":
    # Запускаем основной цикл событий
    asyncio.run(run_collectors())