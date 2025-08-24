# 🤖 Телеграм Бот для Идей

Бот для создания, хранения и получения случайных идей в категориях "Дом" и "Внешний Ивент".

## ✨ Возможности

- 📝 Добавление идей в две категории: Дом и Внешний Ивент
- 🎲 Получение случайных идей (все категории или по отдельности)
- ✅ Отметка идей как выполненных
- 🔄 Регенерация случайных идей
- 📊 Статистика по категориям
- 🐳 Docker контейнеризация
- 🗄️ PostgreSQL база данных

## 🚀 Быстрый запуск

### 1. Клонирование и настройка

```bash
git clone <your-repo>
cd ideas_tg_bot
```

### 2. Создание файла с переменными окружения

```bash
cp env.example .env
```

Отредактируйте `.env` файл, указав ваш токен бота:
```env
BOT_TOKEN=your_actual_bot_token_here
```

### 3. Запуск с Docker Compose

```bash
docker-compose up -d
```

### 4. Проверка работы

```bash
docker-compose logs -f bot
```

## 🛠️ Ручная настройка

### Установка зависимостей

```bash
poetry install
```

### Настройка базы данных

1. Установите PostgreSQL
2. Создайте базу данных:
```sql
CREATE DATABASE ideas_bot;
```

### Запуск бота

```bash
poetry run start
```

## 📱 Команды бота

- `/start` - Начать работу с ботом
- `/add` - Добавить новую идею
- `/random` - Получить случайную идею
- `/stats` - Статистика идей
- `/help` - Справка

## 🏗️ Архитектура

```
bot/
├── __init__.py          # Инициализация пакета
├── config.py            # Конфигурация и переменные окружения
├── database.py          # Работа с PostgreSQL
├── handlers.py          # Обработчики команд
└── main.py             # Точка входа и запуск бота
```

## 🗄️ Структура базы данных

### Таблица `ideas`

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Уникальный идентификатор |
| user_id | BIGINT | ID пользователя Telegram |
| username | TEXT | Имя пользователя |
| category | TEXT | Категория (home/external) |
| description | TEXT | Описание идеи |
| is_completed | BOOLEAN | Статус выполнения |
| created_at | TIMESTAMP | Дата создания |

## 🔧 Настройка окружения

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `BOT_TOKEN` | Токен Telegram бота | - |
| `DB_HOST` | Хост PostgreSQL | localhost |
| `DB_PORT` | Порт PostgreSQL | 5432 |
| `DB_USER` | Пользователь БД | postgres |
| `DB_PASSWORD` | Пароль БД | postgres |
| `DB_NAME` | Имя базы данных | ideas_bot |

## 🐳 Docker команды

### Сборка образа
```bash
docker build -t ideas-bot .
```

### Запуск контейнера
```bash
docker run --env-file .env ideas-bot
```

### Просмотр логов
```bash
docker-compose logs -f bot
```

### Остановка
```bash
docker-compose down
```

## 📝 Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

## 🔍 Отладка

### Логи бота
```bash
docker-compose logs -f bot
```

### Подключение к базе данных
```bash
docker-compose exec postgres psql -U postgres -d ideas_bot
```

### Проверка состояния сервисов
```bash
docker-compose ps
```

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License

## 👨‍💻 Автор

Tarasov Artyom - almtara550@gmail.com
