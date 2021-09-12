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
import logging 
from bot.config import BOT_TOKEN
from bot import LOGGER, database, dispatcher, updater, bot
import bot.newtask_conversation as nw

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text="Hello, this is a todo bot.")
    context.user_data["menu"] = "MainMenu"
    database.add_user(update.effective_user.id, update.effective_user.first_name)
    
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
        records = database.retrieve_all_tasks(update.effective_chat.id) 
        if records != []:
            keyboard = []
            for row in records:
                keyboard.append([InlineKeyboardButton(row[2], callback_data=row[0])])
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=update.effective_chat.id, 
            text="Select a task to see details:", reply_markup=reply_markup)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any tasks yet")
    else:
        query.edit_message_text(text=f"Selected option: {query.data}")

def main() -> None:
    LOGGER.info("Bot Started!")
    
    dispatcher.add_handler(nw.conv_handler)
    dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    updater.start_polling()
    
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
    
main()