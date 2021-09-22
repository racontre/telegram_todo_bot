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
from bot import LOGGER
import bot.database as database
import bot.keyboards as keyboards
import bot.newtask_conversation as nw

TASK_ID, USER_ID, NAME, TIME, STATUS, DESC = range (6)
UPD_NAME, UPD_TIME, UPD_DESC, UPDATE = range(4)
status = {0: 'Unfinished',
          1: 'Done'}

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
    
def update_message(update: Update, context: CallbackContext):
    context.user_data["task_id"] = update.callback_query.data.replace("UpdateID ", "")
    print(context.user_data["task_id"])
    task_id = context.user_data["task_id"]
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

def task_message(update: Update, context: CallbackContext, row):
    """ Takes row (a tuple from the database) and sends the data to user """
    if row is not None:
        keyboard = [
            [
                InlineKeyboardButton("📝 Update", callback_data=f'UpdateID {row[TASK_ID]}'),
                InlineKeyboardButton("🗑 Delete", callback_data=f'DeleteID {row[TASK_ID]}')
            ],
                [ 
                #InlineKeyboardButton("✅ Mark as finished", callback_data=f'FinishedID {row[TASK_ID]}'),
                InlineKeyboardButton("🚨 Turn the reminder on/off", callback_data=f'JobID {row[TASK_ID]}'),
                ]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard) 
        task_string = (f"<b>Name:</b> {row[NAME]}\n"
        #f"<b>Status:</b> {status[row[STATUS]]}\n"
        f"<b>Due:</b> {row[TIME]}\n"
        f"<b>Description:</b> {row[DESC]}\n")
        return reply_markup, task_string
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
        text="Could not output the task")
    pass

def delete_task(update: Update, task_id: int):
    """ Deletes a single task from the database """
    database.delete_task_data(update.effective_chat.id, task_id)
    # job.schedule_removal()
    reply_markup = InlineKeyboardMarkup(keyboards.default)
    update.callback_query.edit_message_text(text=f"The task has been deleted...",
    reply_markup=reply_markup)
    pass

def update_name(update: Update, context: CallbackContext):
    #name = update.message.from_user
    #database.update_task('name', update.effective_chat.id, task_id, name)
    context.bot.send_message(chat_id=update.effective_chat.id, 
    text=f'Hi! Enter the name of your new task. (max {nw.max_name} characters) \n'
    'Send /cancel to stop talking to me.\n\n')
    return UPDATE

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

def update_task(update: Update, context: CallbackContext):
    input = update.message.text
    task_id = context.user_data["task_id"]
    LOGGER.info(f"{task_id}'s new name is {input}")
    return ConversationHandler.END

update_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(callback = update_message, pattern='^UpdateID \d+$'), 
        CallbackQueryHandler(callback = update_name, pattern='^UpdateName \d+$')],
        states={
            UPDATE: [MessageHandler(Filters.text, callback = update_task)],
        },
        fallbacks=[CommandHandler('cancel', nw.cancel)],
    )