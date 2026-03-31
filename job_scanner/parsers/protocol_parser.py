# parsers/protocol_parser.py
from playwright.async_api import async_playwright
import asyncio


async def parse_protocol(keywords, locations):
    async with async_playwright() as p:
        # Запускаем браузер (видим окно)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        all_results = []

        # Сопоставляем твои локации с тем, что понимает сайт в URL
        # На the:protocol локация идет просто словом перед параметрами
        valid_locs = [l.lower() for l in locations if l in ["poland", "germany", "spain", "remote"]]

        for kw in keywords:
            # Превращаем "Python Developer" в "python" для фильтра специализации
            main_tech = kw.split()[0].lower()

            for loc in valid_locs:
                # ФОРМАТ ИЗ ТВОЕЙ ССЫЛКИ:
                # {tech};sp (специализация) / junior;p (уровень) / {loc};lc (локация)
                url = f"https://theprotocol.it/filtry/{main_tech};sp/junior;p/{loc};lc"

                print(f"🔗 Перехожу: {url}")

                try:
                    await page.goto(url, wait_until="networkidle", timeout=30000)
                    await asyncio.sleep(2)  # Даем прогрузиться карточкам

                    # Ищем карточки вакансий
                    # Селектор 'a[href*="/oferta/"]' самый надежный
                    offers = await page.query_selector_all('a[href*="/oferta/"]')

                    for offer in offers:
                        title = await offer.inner_text()
                        link = await offer.get_attribute('href')

                        # Очищаем заголовок (там может быть много лишнего текста из карточки)
                        if title and link:
                            clean_title = title.split('\n')[0].strip()

                            # Проверяем, что это не дубль внутри одной страницы
                            full_url = link if link.startswith("http") else f"https://theprotocol.it{link}"

                            all_results.append({
                                "title": clean_title,
                                "link": full_url,
                                "location": loc.capitalize()
                            })
                            print(f"   ✨ Нашел: {clean_title}")

                except Exception as e:
                    print(f"⚠️ Ошибка на {loc}: {e}")
                    continue

        await browser.close()
        return all_results