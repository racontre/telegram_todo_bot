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
from bot.config import BOT_TOKEN
from bot import LOGGER, database, dispatcher, updater, bot
import bot.newtask_conversation as nw
import bot.tasks as tasks


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text="Hello, this is a todo bot.")
    context.user_data["menu"] = "MainMenu"
    database.create_user(update.effective_user.id, update.effective_user.first_name)
    
    keyboard = [
        [
            InlineKeyboardButton("All Tasks", callback_data='All Tasks'),
            InlineKeyboardButton("Help", callback_data='Help'),
        ],
        [InlineKeyboardButton("New Task", callback_data='New Task')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
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
        tasks.send_user_tasks(update, context)
    elif "TaskID" in query.data:
        task_id = query.data.replace("TaskID", "")
        row = database.retrieve_task_data(update.effective_chat.id, task_id)
        tasks.all_tasks_message(update, context, row)
        pass
    elif "UpdateID" in query.data:
        task_id = query.data.replace("UpdateID", "")
        tasks.update_message(update, context, task_id)
        pass
    elif "DeleteID" in query.data:
        task_id = query.data.replace("DeleteID", "")
        tasks.delete_task(update, task_id)
        query.edit_message_text(text=f"The task has been deleted...")
        pass
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
    LOGGER.info("Bot Started!")
    
    dispatcher.add_handler(nw.conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('alltasks', tasks.send_user_tasks))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
    
main()