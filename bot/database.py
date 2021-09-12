import sqlite3
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

conn = sqlite3.connect(r'C:\Code\telegram_tasker\database.db', check_same_thread=False)
cursor = conn.cursor()

def add_user(user_id: int, user_name: str):
    try:
        cursor.execute('INSERT INTO users (user_id, user_name) VALUES (?, ?)', (user_id, user_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
        
def create_task(user_id: int, task_title: str, due_date: str, desc: str):
    try:
        cursor.execute('INSERT INTO tasks (user_id, task_title, due_date, description) VALUES (?, ?, ?, ?)', 
        (user_id, task_title, due_date, desc))
        conn.commit()
        return True
    except e:
        logger.error(e)
        return False

def retrieve_all_tasks(user_id: int):
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ?"""
    cursor.execute(sqlite_select_query, (user_id,))
    records = cursor.fetchall()
    return records

def retrieve_task_data(user_id: int, task_title: str):
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ? AND task_title = ?"""
    cursor.execute(sqlite_select_query, (user_id, task_title,))
    row = c.fetchone()
    if row == None:
        print("There are no results for this query")
    return row