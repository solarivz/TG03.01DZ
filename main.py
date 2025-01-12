import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("school_bot")

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание базы данных и таблицы students
def init_db():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER NOT NULL,
                        grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Класс состояний для FSM
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

# Обработчик имени
@dp.message(Form.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

# Обработчик возраста
@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            await message.answer("Возраст должен быть положительным числом. Попробуй ещё раз.")
            return
        await state.update_data(age=age)
        await message.answer("В каком ты классе?")
        await state.set_state(Form.grade)
    except ValueError:
        await message.answer("Возраст должен быть числом. Попробуй ещё раз.")

# Обработчик класса
@dp.message(Form.grade)
async def get_grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    # Сохранение данных в базу данных
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''',
                   (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()

    await message.answer(f"Спасибо! Данные сохранены:\nИмя: {user_data['name']}\nВозраст: {user_data['age']}\nКласс: {user_data['grade']}")
    await state.clear()





# Основная функция запуска бота
async def main():
    logging.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот был остановлен!")

