from telegram import InlineKeyboardButton

default = [
        [
            InlineKeyboardButton("All Tasks", callback_data='All Tasks'),
            InlineKeyboardButton("Help", callback_data='Help'),
        ],
        [InlineKeyboardButton("New Task", callback_data='New Task')],
    ]