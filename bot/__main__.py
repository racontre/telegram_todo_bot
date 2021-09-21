from telegram.ext import (
    Updater, 
    CommandHandler, 
    MessageHandler, 
    Filters, 
    CallbackQueryHandler, 
    CallbackContext,
    ConversationHandler
)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from bot.config import BOT_TOKEN
from bot import LOGGER, database, dispatcher, updater, bot
import bot.newtask_conversation as nw
import bot.tasks as tasks
import bot.keyboards as keyboards
import bot.jobs as jobs

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
        task_id = query.data.replace("TaskID ", "")
        row = database.retrieve_task_data(update.effective_chat.id, task_id)
        keyboard, msg = tasks.task_message(update, context, row)
        update.callback_query.edit_message_text(text=msg,  parse_mode=ParseMode.HTML, reply_markup=keyboard)
        pass
    elif "UpdateID" in query.data:
        task_id = query.data.replace("UpdateID ", "")
        tasks.update_message(update, context, task_id)
        pass
    elif "DeleteID" in query.data:
        task_id = query.data.replace("DeleteID ", "")
        tasks.delete_task(update, task_id)
        pass
    elif "!" in query.data:
        task_id = query.data.replace("UpdateName ", "")
        context.user_data["menu"] = "Update Name"
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Send a new name.")
    elif "JobID" in query.data:
        task_id = query.data.replace("JobID ", "")
        exists = jobs.job_exists(update, context, task_id)
        if not exists:
            row = database.retrieve_task_data(update.effective_chat.id, task_id)
            jobs.set_daily_job(update, context, row)
        else:
            jobs.stop_job_queue(update, context, task_id)
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
    LOGGER.info("Bot Started!")
    dispatcher.add_handler(nw.conv_handler)
    dispatcher.add_handler(tasks.update_conversation)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('alltasks', tasks.all_tasks_message))
    dispatcher.add_handler(CommandHandler('set_jobs', jobs.set_all_jobs))    #JOBS
    dispatcher.add_handler(CommandHandler('get_jobs', jobs.get_current_jobs))#JOBS
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
    
main()