import os
import ccxt
import telebot
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(TOKEN)


# Список бирж, настроенных на ФЬЮЧЕРСЫ (Swap)
exchanges = {
    'Binance': ccxt.binance({'options': {'defaultType': 'swap'}}),
    'Bybit': ccxt.bybit({'options': {'defaultType': 'swap'}}),
    'OKX': ccxt.okx({'options': {'defaultType': 'swap'}}),
    'GateIO': ccxt.gateio({'options': {'defaultType': 'swap'}}),
    'Bitget': ccxt.bitget({'options': {'defaultType': 'swap'}})
}


def get_data():
    all_pairs = []

    for name, ex in exchanges.items():
        try:
            print(f"🔄 Опрашиваю {name}...")
            # Загружаем тикеры (цены и изменения)
            tickers = ex.fetch_tickers()

            for symbol, info in tickers.items():
                # Нам нужны только пары к USDT
                if 'USDT' in symbol and info.get('percentage') is not None:
                    pct = float(info['percentage'])
                    last_price = info.get('last', 0)
                    vol = info.get('quoteVolume', 0)

                    # Фильтр: объем торгов больше 100,000$ (чтобы не смотреть мусор)
                    if vol > 100000:
                        # Формируем ссылку на TradingView
                        clean_symbol = symbol.split(':')[0].replace('/', '').replace('USDT', 'USDT')
                        tv_url = f"https://www.tradingview.com/symbols/{clean_symbol}"

                        all_pairs.append({
                            'name': name,
                            'sym': symbol.split(':')[0],
                            'link': tv_url,
                            'change': pct,
                            'price': last_price
                        })
        except Exception as e:
            print(f"⚠️ Ошибка на {name}: {e}")
            continue

    if not all_pairs:
        return "❌ Данные не получены. Проверь интернет или токен."

    # Сортируем по силе движения (от самых волатильных)
    top = sorted(all_pairs, key=lambda x: abs(x['change']), reverse=True)[:10]

    res = "📊 **ТОП ФЬЮЧЕРСОВ (24ч):**\n\n"
    for c in top:
        emoji = "🚀" if c['change'] > 0 else "📉"
        # Формируем кликабельную ссылку Markdown
        res += f"{emoji} [{c['sym']}]({c['link']}) ({c['name']})\n"
        res += f"└ `{c['change']:+.2f}%` | `{c['price']}$` \n\n"

    return res


# Обработка команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я сканер фьючерсов. Напиши /scan, чтобы найти движ.")


# Обработка команды /scan
@bot.message_handler(commands=['scan'])
def scan(message):
    bot.send_message(message.chat.id, "⌛ Мониторю фьючерсы... Подожди 10 сек.")
    try:
        report = get_data()
        # parse_mode='Markdown' делает ссылки синими
        bot.send_message(message.chat.id, report, parse_mode='Markdown', disable_web_page_preview=True)
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка вывода: {e}")


if __name__ == '__main__':
    print("✅ БОТ ЗАПУЩЕН! Напиши /scan в Telegram.")
    bot.infinity_polling()