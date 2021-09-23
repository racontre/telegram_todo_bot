import datetime as dt

from telegram.ext import CallbackContext
from telegram import Update, ParseMode
import pytz #TypeError: Only timezones from the pytz library are supported
from bot import LOGGER, database, updater, bot
from bot import tasks
from bot import keyboards

def get_current_jobs(update: Update, context: CallbackContext):
    job_names = [job.name for job in context.job_queue.jobs()]
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Current jobs: {job_names}")
    return job_names

def job_exists(update: Update, context: CallbackContext, task_id: int):
    job_names = [job.name for job in context.job_queue.jobs()]
    if f'{task_id}' in job_names:
        LOGGER.info(f"Job ID {task_id} exists.")
        return True
    LOGGER.info(f"Job ID {task_id} doesn't exist.")
    return False

def stop_job_queue(update: Update, context: CallbackContext, task_id: int):
    job = context.job_queue.get_jobs_by_name(f"{task_id}")
    job[0].schedule_removal()
    LOGGER.info(f"Job stopped: {task_id}")
    context.bot.send_message(chat_id=update.effective_chat.id,
    text="Job stopped.")

def set_daily_job(update: Update, context: CallbackContext, row):
    def callback_alarm(context: CallbackContext):
        context.bot.send_message(chat_id=context.job.context, text='Test alarm')
        keyboard, msg = tasks.task_message(context.job.context, context, row)
        context.bot.send_message(text=msg,
        parse_mode=ParseMode.HTML, reply_markup=keyboard)
    if row is not [] and not job_exists(update, context, row[tasks.TASK_ID]) and row[tasks.TIME] is not None:
        try:
        ###
            task_time = dt.datetime.strptime(row[tasks.TIME], "%H:%M")
            local = pytz.timezone('Europe/Moscow') #get from db or user data
            naive_dt = dt.datetime(year = 2000, month = 1, day = 1,
            hour=task_time.hour, minute=task_time.minute) #get h and m
            local_dt = local.localize(naive_dt, is_dst = None)
            utc_dt = local_dt.astimezone(pytz.utc)
        ###
            job_daily = updater.job_queue.run_daily(callback_alarm, utc_dt.time(), 
            days=(0, 1, 2, 3, 4, 5, 6), context=row[tasks.USER_ID], name = f'{row[tasks.TASK_ID]}')
            LOGGER.info(f"UTC: {job_daily.next_t}")
            context.bot.send_message(chat_id=update.effective_chat.id,
            text="Job started.")
        except Exception as exception:
            LOGGER.error(f'Could not set daily job: {exception} . The task: {row}')


def set_all_jobs(update: Update, context: CallbackContext):
    records = database.retrieve_all_tasks(update.effective_chat.id)
    if records != []:
        for row in records:
            if row[tasks.TIME] is not None:
                set_daily_job(update, context, row)
