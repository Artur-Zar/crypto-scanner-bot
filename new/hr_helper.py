import re
import os
import logging
from typing import List, Optional

# Настраиваем логирование (уровень INFO — золотой стандарт)
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Константы выносим в начало. Это "конфиг" твоего приложения.
KEYWORDS_TO_SEARCH = [
    "Python", "JavaScript", "React", "SQL", "REST API",
    "Django", "FastAPI", "PostgreSQL", "Git", "Docker", "ChatGPT"
]

def load_vacancy_text(file_path: str) -> Optional[str]:
    """Читает текст вакансии из файла. Возвращает None, если файл не найден."""
    if not os.path.exists(file_path):
        logging.error(f"Файл не найден: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except Exception as e:
        logging.error(f"Ошибка при чтении файла: {e}")
        return None

def extract_technologies(text: str, keywords: List[str]) -> List[str]:
    """Ищет ключевые слова в тексте, используя регулярные выражения."""
    found_techs = []
    for tech in keywords:
        # Используем границы слова \b для точности и re.escape для безопасности
        pattern = rf"\b{re.escape(tech)}\b"
        if re.search(pattern, text, re.IGNORECASE):
            found_techs.append(tech)
    return found_techs

def main() -> None:
    """Основная логика скрипта."""
    # Определяем пути
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vacancy_file = os.path.join(current_dir, "vacancy.txt")

    # 1. Загрузка данных
    content = load_vacancy_text(vacancy_file)
    if not content:
        return

    logging.info(f"Начинаю анализ файла: {os.path.basename(vacancy_file)}")

    # 2. Обработка
    results = extract_technologies(content, KEYWORDS_TO_SEARCH)

    # 3. Вывод результата
    print("\n" + "="*40)
    print("📋 РЕЗУЛЬТАТ АНАЛИЗА СТЕКА:")
    print("="*40)

    if results:
        for tech in sorted(results):
            print(f"  [+] {tech}")
        print(f"\nВсего найдено: {len(results)} технологий.")
    else:
        print("  [-] Совпадений не обнаружено.")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()