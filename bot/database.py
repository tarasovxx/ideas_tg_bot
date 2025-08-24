import asyncpg
from typing import Optional
from .config import DatabaseConfig

class Database:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создает пул соединений с базой данных"""
        self.pool = await asyncpg.create_pool(
            host=self.config.host,
            port=self.config.port,
            user=self.config.user,
            password=self.config.password,
            database=self.config.database
        )

    async def close(self):
        """Закрывает пул соединений"""
        if self.pool:
            await self.pool.close()

    async def init_tables(self):
        """Инициализирует таблицы базы данных"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS ideas (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    username TEXT,
                    category TEXT NOT NULL CHECK (category IN ('home', 'external')),
                    description TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    async def add_idea(self, user_id: int, username: str, category: str, description: str) -> int:
        """Добавляет новую идею в базу данных"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO ideas (user_id, username, category, description)
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, user_id, username, category, description)
            return row['id']

    async def get_random_idea(self, category: Optional[str] = None) -> Optional[dict]:
        """Получает случайную идею из базы данных"""
        async with self.pool.acquire() as conn:
            if category:
                row = await conn.fetchrow("""
                    SELECT id, user_id, username, category, description, created_at
                    FROM ideas
                    WHERE category = $1 AND is_completed = FALSE
                    ORDER BY RANDOM()
                    LIMIT 1
                """, category)
            else:
                row = await conn.fetchrow("""
                    SELECT id, user_id, username, category, description, created_at
                    FROM ideas
                    WHERE is_completed = FALSE
                    ORDER BY RANDOM()
                    LIMIT 1
                """)
            
            if row:
                return dict(row)
            return None

    async def mark_idea_completed(self, idea_id: int) -> bool:
        """Помечает идею как выполненную"""
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                UPDATE ideas
                SET is_completed = TRUE
                WHERE id = $1
            """, idea_id)
            return result == "UPDATE 1"

    async def get_ideas_count(self, category: Optional[str] = None) -> int:
        """Получает количество невыполненных идей"""
        async with self.pool.acquire() as conn:
            if category:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM ideas
                    WHERE category = $1 AND is_completed = FALSE
                """, category)
            else:
                count = await conn.fetchval("""
                    SELECT COUNT(*) FROM ideas
                    WHERE is_completed = FALSE
                """)
            return count
