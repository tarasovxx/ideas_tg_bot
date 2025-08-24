import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from .config import load_config
from .database import Database
from .handlers import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    # Загружаем конфигурацию
    config = load_config()
    
    if not config.token:
        logger.error("BOT_TOKEN не установлен в переменных окружения!")
        return
    
    # Инициализируем бота и диспетчер
    bot = Bot(token=config.token)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Инициализируем базу данных
    db = Database(config.database)
    
    # Подключаемся к базе данных
    try:
        await db.connect()
        await db.init_tables()
        logger.info("База данных успешно подключена и инициализирована")
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return
    
    # Регистрируем роутеры
    dp.include_router(router)
    
    # Внедряем базу данных в диспетчер
    dp["db"] = db
    
    # Запускаем бота
    try:
        logger.info("Бот запускается...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        # Закрываем соединения
        await db.close()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
