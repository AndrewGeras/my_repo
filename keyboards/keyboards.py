from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove)
from lexicon.lexicon import LEXICON_BTN

yes_button = InlineKeyboardButton(
        text='✅ Да',
        callback_data='yes'
    )
no_button = InlineKeyboardButton(
        text='❌ Нет',
        callback_data='no'
    )
yes_no_keyboard: list[list[InlineKeyboardButton]] = [
    [yes_button, no_button]
    ]
yes_no_kb_markup = InlineKeyboardMarkup(inline_keyboard=yes_no_keyboard)


#  создаём кнопку отмены для произвольного выхода из режима добавления слов
stop_button = KeyboardButton(text=LEXICON_BTN['stop_button'])
stop_keyboard = ReplyKeyboardMarkup(
        keyboard=[[stop_button]],
        resize_keyboard=True,
    )


#  создаём клавиатуру для выбора способа тестирования "по словам" или "по значениям"
by_word_btn = InlineKeyboardButton(
    text='По словам',
    callback_data='by_word'
)
by_mean_btn = InlineKeyboardButton(
    text='По значениям',
    callback_data='by_meaning'
)
word_mean_kb_markup = InlineKeyboardMarkup(inline_keyboard=[[by_word_btn, by_mean_btn]])