import asyncio
import aiohttp
from aiogram import Bot, Dispatcher
from bs4 import BeautifulSoup
import os

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL")

# --- Создание бота ---
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# --- Список просмотренных объявлений ---
seen_ids = set()

async def fetch_cian():
    url = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&region=2&room1=1&room2=1&room3=1&room4=1&is_secondary=1&minarea=20&maxprice=20000000&currency=2&foot_min=10&object_type%5B0%5D=1&only_flat=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            cards = soup.select("article._93444fe79c--card--ibP42")
            for card in cards:
                link = card.select_one("a._93444fe79c--link--eoxce")
                if not link:
                    continue

                href = link['href']
                full_url = f"https://www.cian.ru{href}" if href.startswith("/") else href

                if full_url in seen_ids:
                    continue

                seen_ids.add(full_url)

                title = card.get_text(separator="\n").strip()
                await bot.send_message(TELEGRAM_CHANNEL_ID, f"\ud83d\udd39 Новая квартира:\n{title}\n{full_url}")

async def check_loop():
    while True:
        try:
            await fetch_cian()
        except Exception as e:
            print(f"\u274c Ошибка парсинга: {e}")
        await asyncio.sleep(600)

async def main():
    asyncio.create_task(check_loop())
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())