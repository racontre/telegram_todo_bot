import sqlite3
import os
from bot import LOGGER

conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + '\database.db', check_same_thread=False)
cursor = conn.cursor()

def create_user(user_id: int, user_name: str):
    try:
        sqlite_insert_query = """INSERT INTO users (user_id, user_name) VALUES (?, ?)"""
        cursor.execute(sqlite_insert_query, (user_id, user_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
        
def create_task(user_id: int, task_title: str, due_date: str, desc: str):
    sqlite_insert_query = """INSERT INTO tasks (user_id, task_title, due_date, description) VALUES (?, ?, ?, ?)"""
    try:
        cursor.execute(sqlite_insert_query, (user_id, task_title, due_date, desc))
        conn.commit()
        return True
    except Exception as e:
        LOGGER.error("Unable to create a task: ", e)
        return False

def retrieve_all_tasks(user_id: int):
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ?"""
    try:
        cursor.execute(sqlite_select_query, (user_id,))
        records = cursor.fetchall()
    except Exception as e:
        LOGGER.info(f"Unable to retrieve tasks for User ID {user_id}: ", e)
        return None
    return records

def retrieve_global_tasks():
    sqlite_select_query = """SELECT * from tasks"""
    try:
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except Exception as e:
        LOGGER.info(f"Unable to retrieve tasks: ", e)
        return None
    return records

def retrieve_task_data(user_id: int, task_id: int):
    """Returns a single task. The task_id is unique in the database"""
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_select_query, (user_id, task_id,))
        row = cursor.fetchall()
        LOGGER.info(f"A result for TaskID {task_id} and UserID {user_id} has been found")
        return row[0]
    except Exception as e:
        LOGGER.info(f"Unable to retrieve Task ID {task_id}: ", e)
        return None
    if row == None:
        LOGGER.info(f"There are no results for TaskID {task_id} and UserID {user_id}")
    return row

def update_task(column_name: str, user_id: int, task_id: int, name: str):
    sqlite_update_query = """UPDATE tasks SET ? = ? WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_update_query, (column_name, name, user_id, task_id))
        conn.commit()
        LOGGER.info(f"Task ID {task_id} has been updated. ({column_name})")
    except Exception as e:
        LOGGER.info(f"Unable to update {column_name} for Task ID {task_id}: ", e)
    pass
    
def delete_task_data(user_id: int, task_id: int):
    sqlite_delete_query = """DELETE FROM tasks WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_delete_query, (user_id, task_id,))
        conn.commit()
        LOGGER.info(f"Task ID {task_id} has been deleted.")
    except Exception as e:
        LOGGER.info(f"Unable to delete Task ID {task_id}: ", e)