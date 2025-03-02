import logging
import schedule
import time
import asyncio
import os
from telegram import Bot
from telegram.request import HTTPXRequest
from openai import OpenAI
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение токена бота, ID группы, ID потока и ключа OpenAI из переменных окружения
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
THREAD_ID = os.getenv("THREAD_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Инициализация Telegram-бота
request = HTTPXRequest()  # Убираем timeout, так как он не поддерживается
bot = Bot(token=TOKEN, request=request)

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_image():
    """Генерация изображения с помощью DALL·E 2."""
    prompt = (
        "A breathtaking futuristic nature landscape, vibrant and colorful, combining stunning natural beauty "
        "with advanced hydrogen energy technology. Imagine lush green valleys, crystal-clear lakes, and majestic mountains, "
        "harmoniously integrated with sleek, innovative hydrogen-powered infrastructure. "
        "The scene radiates purity and progress, with shimmering hydrogen fuel cells and clean energy systems subtly embedded in the environment. "
        "No wind turbines, no solar panels – just a seamless fusion of nature and advanced sustainable technology, illuminated by ethereal lighting."
    )

    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        n=1,
        size="1024x1024",
        timeout=60  # Если библиотека OpenAI поддерживает этот параметр
    )

    return response.data[0].url

async def send_image():
    """Отправка изображения в Telegram-группу в заданный поток."""
    try:
        image_url = generate_image()
        await bot.send_photo(chat_id=CHAT_ID, message_thread_id=THREAD_ID, photo=image_url)
        logging.info("Изображение отправлено успешно.")
    except Exception as e:
        logging.error(f"Ошибка при отправке изображения: {e}")

def schedule_task():
    """Обертка для запуска асинхронной функции в синхронном коде."""
    asyncio.run(send_image())

# Планирование задачи на выполнение в указанное время
schedule.every().day.at("18:42").do(schedule_task)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Бот запущен...")

    while True:
        schedule.run_pending()
        time.sleep(60)
