import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from analyzer import BookAnalyzer

# загружаем ключи из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# логирование, чтобы видеть ошибки
logging.basicConfig(level=logging.INFO)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

book_analyzer = BookAnalyzer(mistral_api_key=MISTRAL_API_KEY)

# /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "📚 Привет! Я Book-Analyzer бот.\n\n"
        "Пришли мне название книги и автора в любом формате, "
        "а я проанализирую её и пришлю структурированный обзор.\n\n"
        "Например: «Преступление и наказание - Фёдор Достоевский»"
    )

# /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "❔ Как я работаю?\n"
        "1. Ты присылаешь мне название книги и автора.\n"
        "2. Я ищу информацию в интернете (через DuckDuckGo).\n"
        "3. Возвращаю готовый анализ, подготовленный с помощью Mistral AI."
    )

# обработчик любого текстового сообщения
@dp.message()
async def analyze_book_message(message: Message):
    # текст от пользователя
    user_text = message.text
    
    # отправляем реакцию, что начали работу
    await message.answer("Подождите, анализирую книгу.... Это может занять от нескольких секунд до нескольких минут.\nВ изучении чего-то важного требуется время 🍃")

    book = user_text
    try:
        result = book_analyzer.analyze_book(book)
        await message.answer(result) # отправляем результат пользователю
        
    except Exception as e:
        # если что-то пошло не так, ловим ошибку и пишем пользователю
        logging.error(f"Ошибка при анализе: {e}")
        await message.answer(
            "Произошла ошибка при анализе книги. Пожалуйста, попробуй ещё раз "
            "или убедись, что ты правильно написал(а) название и автора."
        )


# запуск бота
async def main():
    print("---------------------Бот готов к работе!----------------------")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())