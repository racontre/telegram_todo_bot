from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler, 
    Filters,
    ConversationHandler,
    CallbackContext,
)
import bot.database as database
import bot.keyboards as keyboards

TASK_ID, USER_ID, NAME, TIME, STATUS, DESC = range (6)

def all_tasks_message(update: Update, context: CallbackContext):
    records = database.retrieve_all_tasks(update.effective_chat.id) 
    if records != []:
        keyboard = []
        for row in records:
            keyboard.append([InlineKeyboardButton(row[2], callback_data=f"TaskID {row[TASK_ID]}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Select a task to see details:", reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="You don't have any tasks yet")
    pass
    
def update_message(update: Update, context: CallbackContext, task_id: int):
    keyboard = [
    [
            InlineKeyboardButton("Name", callback_data='UpdateName ' + str(task_id)),
            InlineKeyboardButton("Time", callback_data='UpdateTime ' + str(task_id)),
    ],
    [
            InlineKeyboardButton("Description", callback_data='UpdateDesc' + str(task_id)),
            InlineKeyboardButton("Back", callback_data='TaskID ' + str(task_id))
    ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text="Я потом это сделаю мне пока неинтересно", reply_markup=reply_markup)
    pass

def send_task(update: Update, context: CallbackContext, row):
    """ Takes row (a tuple from the database) and sends the data to user """
    if row is not None:
        keyboard = [
            [
                #InlineKeyboardButton("📝 Update", callback_data=f'UpdateID {row[TASK_ID]}'),
                InlineKeyboardButton("🗑 Delete", callback_data=f'DeleteID {row[TASK_ID]}')
            ],
                [ 
                InlineKeyboardButton("✅ Mark as finished", callback_data=f'FinishedID {row[TASK_ID]}'),
                
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard) 
        task_string = f"<b>Name:</b> {row[NAME]}"
                        f"<b>Status:</b> {row[STATUS]}"
                        f"<b>Due:</b> {row[TIME]}"
                        f"<b>Description:</b> {row[DESC]}"
        update.callback_query.edit_message_text(text=task_string, 
        parse_mode=ParseMode.HTML, reply_markup=reply_markup)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Could not output the task")
    pass

def delete_task(update: Update, task_id: int):
    """ Deletes a single task from the database """
    database.delete_task_data(update.effective_chat.id, task_id)
    
    reply_markup = InlineKeyboardMarkup(keyboards.default)
    update.callback_query.edit_message_text(text=f"The task has been deleted...",
    reply_markup=reply_markup)
    pass

def update_name(update: Update, context: CallbackContext, task_id: int):
    name = update.message.from_user
    database.update_task('name', update.effective_chat.id, task_id, name)
    pass

def update_state(update: Update, context: CallbackContext):
    pass
    
def update_desc(update: Update, context: CallbackContext, task_id: int):
    desc = update.message.from_user
    database.update_task('desc', update.effective_chat.id, task_id, name)
    pass

def update_time(update: Update, context: CallbackContext, time: str):
    time = update.message.from_user
    database.update_task('time', update.effective_chat.id, task_id, name)
    pass
    
"""update_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback = update_message, pattern='^UpdateID \d+$')],
        states={
            NAME: [MessageHandler(Filters.regex(^{1, 20}$) & ~Filters.command, update_name)],
            TIME: [MessageHandler(Filters.regex(^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$) & 
            ~Filters.command, update_time)],
            DESC: [MessageHandler(Filters.regex(^{1, 100}$) & ~Filters.command, update_desc)]
            
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )"""