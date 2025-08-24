from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .database import Database

router = Router()

class IdeaStates(StatesGroup):
    waiting_for_category = State()
    waiting_for_description = State()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "Привет! Я бот для идей. Вот что я умею:\n\n"
        "📝 /add - Добавить новую идею\n"
        "🎲 /random - Получить случайную идею\n"
        "📊 /stats - Статистика идей\n"
        "❓ /help - Помощь"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Бот для идей - Помощь</b>

<b>Команды:</b>
• /start - Начать работу с ботом
• /add - Добавить новую идею
• /random - Получить случайную идею
• /stats - Статистика идей
• /help - Показать эту справку

<b>Категории идей:</b>
• 🏠 Дом - идеи для дома
• 🌍 Внешний Ивент - идеи для внешних мероприятий

<b>Как использовать:</b>
1. Добавьте идею командой /add
2. Выберите категорию
3. Напишите описание идеи
4. Получайте случайные идеи командой /random
5. Помечайте выполненные идеи
    """
    await message.answer(help_text, parse_mode="HTML")

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """Обработчик команды /add - начало добавления идеи"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏠 Дом", callback_data="category_home")
    builder.button(text="🌍 Внешний Ивент", callback_data="category_external")
    builder.adjust(2)
    
    await message.answer(
        "Выберите категорию для вашей идеи:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(IdeaStates.waiting_for_category)

@router.callback_query(F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора категории"""
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    
    category_names = {
        "home": "🏠 Дом",
        "external": "🌍 Внешний Ивент"
    }
    
    await callback.message.edit_text(
        f"Выбрана категория: {category_names[category]}\n\n"
        "Теперь напишите описание вашей идеи:"
    )
    await state.set_state(IdeaStates.waiting_for_description)

@router.message(IdeaStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext, db: Database):
    """Обработчик ввода описания идеи"""
    data = await state.get_data()
    category = data["category"]
    description = message.text
    
    try:
        idea_id = await db.add_idea(
            user_id=message.from_user.id,
            username=message.from_user.username or message.from_user.first_name,
            category=category,
            description=description
        )
        
        category_names = {
            "home": "🏠 Дом",
            "external": "🌍 Внешний Ивент"
        }
        
        await message.answer(
            f"✅ Идея успешно добавлена!\n\n"
            f"📝 <b>Описание:</b> {description}\n"
            f"🏷️ <b>Категория:</b> {category_names[category]}\n"
            f"🆔 <b>ID:</b> {idea_id}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        await message.answer("❌ Произошла ошибка при добавлении идеи. Попробуйте позже.")
        print(f"Error adding idea: {e}")
    
    await state.clear()

@router.message(Command("random"))
async def cmd_random(message: Message, db: Database):
    """Обработчик команды /random - получение случайной идеи"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Случайная идея", callback_data="random_any")
    builder.button(text="🏠 Только дом", callback_data="random_home")
    builder.button(text="🌍 Только внешний", callback_data="random_external")
    builder.adjust(1)
    
    await message.answer(
        "Выберите тип случайной идеи:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("random_"))
async def process_random_selection(callback: CallbackQuery, db: Database):
    """Обработчик выбора типа случайной идеи"""
    random_type = callback.data.split("_")[1]
    
    if random_type == "any":
        category = None
        category_text = "любой категории"
    elif random_type == "home":
        category = "home"
        category_text = "🏠 Дом"
    else:
        category = "external"
        category_text = "🌍 Внешний Ивент"
    
    idea = await db.get_random_idea(category)
    
    if not idea:
        await callback.message.edit_text(
            f"😔 Идей в категории {category_text} пока нет.\n"
            "Добавьте первую идею командой /add!"
        )
        return
    
    category_names = {
        "home": "🏠 Дом",
        "external": "🌍 Внешний Ивент"
    }
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Выполнено", callback_data=f"complete_{idea['id']}")
    builder.button(text="🔄 Другая идея", callback_data=f"regenerate_{random_type}")
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"🎲 <b>Случайная идея {category_text}:</b>\n\n"
        f"📝 <b>Описание:</b> {idea['description']}\n"
        f"👤 <b>Автор:</b> @{idea['username']}\n"
        f"📅 <b>Добавлена:</b> {idea['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        f"🆔 <b>ID:</b> {idea['id']}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("complete_"))
async def process_complete_idea(callback: CallbackQuery, db: Database):
    """Обработчик отметки идеи как выполненной"""
    idea_id = int(callback.data.split("_")[1])
    
    try:
        success = await db.mark_idea_completed(idea_id)
        if success:
            await callback.message.edit_text(
                "✅ Идея помечена как выполненная!\n\n"
                "🎉 Поздравляем с выполнением!"
            )
        else:
            await callback.message.edit_text("❌ Не удалось отметить идею как выполненную.")
    except Exception as e:
        await callback.message.edit_text("❌ Произошла ошибка. Попробуйте позже.")
        print(f"Error completing idea: {e}")

@router.callback_query(F.data.startswith("regenerate_"))
async def process_regenerate_idea(callback: CallbackQuery, db: Database):
    """Обработчик регенерации случайной идеи"""
    random_type = callback.data.split("_")[1]
    
    if random_type == "any":
        category = None
        category_text = "любой категории"
    elif random_type == "home":
        category = "home"
        category_text = "🏠 Дом"
    else:
        category = "external"
        category_text = "🌍 Внешний Ивент"
    
    idea = await db.get_random_idea(category)
    
    if not idea:
        await callback.message.edit_text(
            f"😔 Больше идей в категории {category_text} нет.\n"
            "Добавьте новые идеи командой /add!"
        )
        return
    
    category_names = {
        "home": "🏠 Дом",
        "external": "🌍 Внешний Ивент"
    }
    
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Выполнено", callback_data=f"complete_{idea['id']}")
    builder.button(text="🔄 Другая идея", callback_data=f"regenerate_{random_type}")
    builder.adjust(2)
    
    await callback.message.edit_text(
        f"🎲 <b>Новая случайная идея {category_text}:</b>\n\n"
        f"📝 <b>Описание:</b> {idea['description']}\n"
        f"👤 <b>Автор:</b> @{idea['username']}\n"
        f"📅 <b>Добавлена:</b> {idea['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        f"🆔 <b>ID:</b> {idea['id']}",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database):
    """Обработчик команды /stats - статистика идей"""
    try:
        total_count = await db.get_ideas_count()
        home_count = await db.get_ideas_count("home")
        external_count = await db.get_ideas_count("external")
        
        stats_text = f"""
📊 <b>Статистика идей:</b>

🎯 <b>Всего активных идей:</b> {total_count}
🏠 <b>Идеи для дома:</b> {home_count}
🌍 <b>Внешние идеи:</b> {external_count}

💡 Добавляйте новые идеи командой /add
🎲 Получайте случайные идеи командой /random
        """
        
        await message.answer(stats_text, parse_mode="HTML")
        
    except Exception as e:
        await message.answer("❌ Не удалось получить статистику. Попробуйте позже.")
        print(f"Error getting stats: {e}")
