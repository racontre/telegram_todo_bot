from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters, 
    CallbackQueryHandler, 
    CallbackContext,
    ConversationHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import datetime as dt
import pytz #TypeError: Only timezones from the pytz library are supported
from bot.config import BOT_TOKEN
from bot import LOGGER, database, dispatcher, updater, bot
import bot.newtask_conversation as nw
import bot.tasks as tasks
import bot.keyboards as keyboards

def callback_alarm(context):
     context.bot.send_message(chat_id=context.job.context, text='Test alarm')

def daily_callback_timer(update: Update, context: CallbackContext, row):
    context.bot.send_message(chat_id=update.effective_chat.id,
                      text='Test timer')
    try:
    ###
        task_time = dt.datetime.strptime(row[tasks.TIME], "%H:%M")
        print(task_time)
        local = pytz.timezone('Europe/Moscow') #get from db or user data
        naive_dt = dt.datetime(year = 2000, month = 1, day = 1, 
        hour=task_time.hour, minute=task_time.minute) #get h and m
        local_dt = local.localize(naive_dt, is_dst = None)
        utc_dt = local_dt.astimezone(pytz.utc)
    ###
        jobDaily = updater.job_queue.run_daily(callback_alarm, utc_dt.time(), 
        days=(0, 1, 2, 3, 4, 5, 6), context=row[tasks.USER_ID])
        print(jobDaily.next_t)
    except Exception as e:
        LOGGER.error(f'Could not set job: {e} for {row}')


def set_all_jobs(update: Update, context: CallbackContext):
    records = database.retrieve_all_tasks(update.effective_chat.id)
    if records != []:
        for row in records:
            if row[tasks.TIME] is not None:
                daily_callback_timer(update, context, row)
    pass

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text="Hello, this is a todo bot.")
    context.user_data["menu"] = "MainMenu"
    database.create_user(update.effective_user.id, update.effective_user.first_name)
    reply_markup = InlineKeyboardMarkup(keyboards.default)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    
    if query.data == "New Task":
        pass
    elif query.data == "All Tasks":
        tasks.all_tasks_message(update, context)
    elif "TaskID" in query.data:
        task_id = query.data.replace("TaskID", "")
        row = database.retrieve_task_data(update.effective_chat.id, task_id)
        tasks.send_task(update, context, row)
        pass
    elif "UpdateID" in query.data:
        task_id = query.data.replace("UpdateID", "")
        tasks.update_message(update, context, task_id)
        pass
    elif "DeleteID" in query.data:
        task_id = query.data.replace("DeleteID", "")
        tasks.delete_task(update, task_id)
        pass
    elif "UpdateName" in query.data:
        task_id = query.data.replace("UpdateName", "")
        context.user_data["menu"] = "Update Name"
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Send a new name.")
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
    LOGGER.info("Bot Started!")
    dispatcher.add_handler(nw.conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('alltasks', tasks.all_tasks_message))
    dispatcher.add_handler(CommandHandler('jobs', set_all_jobs))
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
    
main()