import sqlite3

DATABASE = 'game_store.db' # Имя вашей базы данных

def get_db():
    """Устанавливает соединение с базой данных."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Используем Row для доступа к столбцам по имени
    return conn

def close_db(conn):
    """Закрывает соединение с базой данных."""
    conn.close()

def init_db():
    """Инициализирует базу данных, выполняя скрипт из schema.sql."""
    with get_db() as db:
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
            db.commit() # Сохраняем изменения

if __name__ == '__main__':
    init_db() # Создаем базу данных если запускаем этот файл