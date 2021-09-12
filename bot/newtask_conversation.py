#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import bot.database

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler, 
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

NAME, DATE, DESC = range(3)


def newtask(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text='Hi! Enter the name of your new task. '
        'Send /cancel to stop talking to me.\n\n')
    return NAME


def name(update: Update, context: CallbackContext) -> int:
    """Stores the name and asks for a due date."""
    user = update.message.from_user
    logger.info("New task by %s: %s", user.first_name, update.message.text)
    context.user_data["name"] = update.message.text
    update.message.reply_text(
        'I see! Does the task have a due date? '
        'I can send you a reminder for this task, or send /skip if you don\'t want to.',
        reply_markup=ReplyKeyboardRemove(),
    )
    return DATE


def date(update: Update, context: CallbackContext) -> int:
    """Stores the due date and asks for a description."""
    user = update.message.from_user
    logger.info("%s entered date: %s", user.first_name, update.message.text)
    context.user_data["date"] = update.message.text
    update.message.reply_text(
        'Gorgeous! Now, describe the task please, or send /skip if you don\'t want to.'
    )

    return DESC


def skip_date(update: Update, context: CallbackContext) -> int:
    """Skips the photo and asks for a location."""
    user = update.message.from_user
    context.user_data["date"] = ""
    logger.info("User %s did not set a date.", user.first_name)
    update.message.reply_text(
        'Now, describe your task please, or send /skip.'
    )

    return DESC


def desc(update: Update, context: CallbackContext) -> int:
    """Stores the location and asks for some info about the user."""
    user = update.message.from_user
    logger.info(
        "%s' description of the task: %s", user.first_name, update.message.text)
    context.user_data["desc"] = update.message.text
    update.message.reply_text(
        'Sending...'
    )
    save_task(update, context)
    return ConversationHandler.END


def skip_desc(update: Update, context: CallbackContext) -> int:
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    logger.info("User %s did not set a description.", user.first_name)
    context.user_data["desc"] = ""
    update.message.reply_text(
        'Sending...'
    )
    save_task(update, context)
    return ConversationHandler.END

def save_task(update: Update, context: CallbackContext) -> int:
    """ Sends the data to the database. """
    user_id = update.effective_chat.id
    task_title = context.user_data['name']
    due_date = context.user_data['date']
    desc = context.user_data['desc']
    if (database.create_task(user_id, task_title, due_date, desc)):
        update.message.reply_text(
            'Done'
        )
    else:
        update.message.reply_text(
            'Task creation failed'
        )
    print (context.user_data)
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
    
conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newtask', newtask), 
            CallbackQueryHandler(callback  = newtask, pattern='^New Task?')],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            DATE: [MessageHandler(Filters.text & ~Filters.command, date), 
                    CommandHandler('skip', skip_date)
                    ],
            DESC: [MessageHandler(Filters.text & ~Filters.command, desc),
                    CommandHandler('skip', skip_desc)
                    ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()