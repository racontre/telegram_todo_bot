import sqlite3
import os
from bot import LOGGER

conn = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) +
        r'\database.db', check_same_thread=False)
cursor = conn.cursor()

def create_user(user_id: int, user_name: str):
    try:
        sqlite_insert_query = """INSERT INTO users (user_id, user_name) VALUES (?, ?)"""
        cursor.execute(sqlite_insert_query, (user_id, user_name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass

def create_task(user_id: int, task_title: str, due_date: str, desc: str):
    sqlite_insert_query = """INSERT INTO tasks (user_id, task_title, due_date, description) 
VALUES (?, ?, ?, ?)"""
    try:
        cursor.execute(sqlite_insert_query, (user_id, task_title, due_date, desc))
        conn.commit()
        return True
    except Exception as exception:
        LOGGER.error("Unable to create a task: %s", exception)
        return False

def retrieve_all_tasks(user_id: int):
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ?"""
    try:
        cursor.execute(sqlite_select_query, (user_id,))
        records = cursor.fetchall()
    except Exception as exception:
        LOGGER.info("Unable to retrieve tasks for User ID %s: %s", user_id, exception)
        return None
    return records

def retrieve_global_tasks():
    sqlite_select_query = """SELECT * from tasks"""
    try:
        cursor.execute(sqlite_select_query)
        records = cursor.fetchall()
    except Exception as exception:
        LOGGER.info("Unable to retrieve tasks: %s", exception)
        return None
    return records

def retrieve_task_data(user_id: int, task_id: int):
    """Returns a single task. The task_id is unique in the database"""
    sqlite_select_query = """SELECT * from tasks WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_select_query, (user_id, task_id,))
        row = cursor.fetchall()
        LOGGER.info("A result for TaskID %s and UserID %s has been found", task_id, user_id)
        return row[0]
    except Exception as exception:
        LOGGER.info("Unable to retrieve Task ID %s: %s ", task_id, exception)
        return None
    if row is None:
        LOGGER.info(f"There are no results for TaskID %s and UserID %s", task_id,  user_id)
    return row

def update_task(column_name: str, user_id: int, task_id: int, name: str):
    sqlite_update_query = """UPDATE tasks SET ? = ? WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_update_query, (column_name, name, user_id, task_id))
        conn.commit()
        LOGGER.info("Task ID %s has been updated. (%s)", task_id, column_name)
    except Exception as exception:
        LOGGER.info("Unable to update %s for Task ID %s: %s", column_name, task_id, exception)


def delete_task_data(user_id: int, task_id: int):
    sqlite_delete_query = """DELETE FROM tasks WHERE user_id = ? AND task_id = ?"""
    try:
        cursor.execute(sqlite_delete_query, (user_id, task_id,))
        conn.commit()
        LOGGER.info("Task ID %s has been deleted.", task_id)
    except Exception as exception:
        LOGGER.info(f"Unable to delete Task ID %s: %s", task_id, exception)
