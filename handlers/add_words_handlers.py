from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from lexicon.lexicon import LEXICON, LEXICON_ADD, LEXICON_BTN
from users_data.users import check_user_in_list, add_user_to_list
from states.states import FSMAddWords
from filters.filters import IsLatinLetters
from keyboards.keyboards import yes_no_kb_markup, stop_keyboard
from utils.utils import save_data, word_in_data
from json import dump


router = Router()

storage = MemoryStorage()


@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    uid = message.from_user.id
    if check_user_in_list(uid):
        await message.answer(text=f"Рад Вас снова видеть {message.from_user.first_name}!\n"
                                  f"\n{LEXICON['user_greeting']}",
                             reply_markup=stop_keyboard)

    else:
        add_user_to_list(uid)
        with open(f'users_data/vocabularies/{str(uid)}.json', 'x', encoding='utf-8') as file:
            dump({}, file)
        await message.answer(text=f"👋🏻Привет {message.from_user.first_name}!\n"
                              f"\n{LEXICON['new_user_greeting']}",
                             reply_markup=stop_keyboard)


# Хендлер обрабатывающий отправку команды "Добавить слова"
@router.message(Command(commands='add_word'), StateFilter(default_state))
async def process_add_word_command(message: Message, state: FSMContext):

    await message.answer(
        text=f"{LEXICON_ADD['which_word']}"
    )
    await state.set_state(FSMAddWords.word_adding)
    await message.delete()


# хендлер обрабатывающий ввод слова латиницей в режиме добавления слова в словарь
@router.message(StateFilter(FSMAddWords.word_adding), IsLatinLetters())
async def process_input_latin_word_in_adding(message: Message, state: FSMContext):
    word = message.text.lower()
    uid = message.from_user.id
    meaning = word_in_data(uid, word)
    if meaning:
        text = f"{LEXICON_ADD['word_in_data']}<b><i>{word}</i></b>.\n\n" \
               f"Оно значит: <b><i>{', '.join(meaning)}</i></b>.\n\n" \
               f"{LEXICON_ADD['ask_about_add_mng']}<b><i>{word}</i></b>?"
        await message.answer(text=text, reply_markup=yes_no_kb_markup)
        await state.update_data(word=word, meaning=meaning)
        await state.set_state(FSMAddWords.wait_yn_btn_mean)
    else:
        await state.update_data(word=word, meaning=[])
        await message.answer(text=f"{LEXICON_ADD['which_mng']} <b><i>{word}</i></b>?")
        await state.set_state(FSMAddWords.mean_adding)


# хендлер обрабатывающий ввод слова не латиницей в режиме добавления слова в словарь
@router.message(StateFilter(FSMAddWords.word_adding), ~IsLatinLetters())
async def warning_nonlating_input(message:Message):
    await message.answer(text=LEXICON_ADD['nonlatin_input'])


# хендлер обрабатывающий ввод текстового сообщения для добавления значения слова в словаре
@router.message(StateFilter(FSMAddWords.mean_adding), F.text and F.text.isalpha())
async def process_input_meaning(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text.lower() in data['meaning']:
        await message.answer(
            text=f"{LEXICON_ADD['mean_in_data']}<b><i>{data['word']}</i></b>?",
            reply_markup=yes_no_kb_markup
        )
    else:
        data['meaning'].append(message.text.lower())
        await state.set_data(data)

        await message.answer(
            text=f"{LEXICON_ADD['ask_about_add_mng']}<b><i>{data['word']}</i></b>?",
            reply_markup=yes_no_kb_markup
        )
    await state.set_state(FSMAddWords.wait_yn_btn_mean)


# хендлер обрабаотывающий ввод нетекстового значения слова в словарь
@router.message(StateFilter(FSMAddWords.mean_adding), ~(F.text and F.text.isalpha()))
async def warning_bad_meaning_input(message:Message):
    await message.answer(text=LEXICON_ADD['bad_meaning'])


# хендлер обрабатывающий нажатие кнопки "Да" для ввода дополнительного значения слова
@router.callback_query(StateFilter(FSMAddWords.wait_yn_btn_mean), F.data == 'yes')
async def process_yes_button_press(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.message.edit_text(text=f"{LEXICON_ADD['which_mng']} <b><i>{data['word']}</i></b>?")
    await state.set_state(FSMAddWords.mean_adding)


# хендлер обрабатывающий нажатие кнопки "Нет для ввода дополнительного значения слова
@router.callback_query(StateFilter(FSMAddWords.wait_yn_btn_mean), F.data == 'no')
async def stop_adding_meaning(callback: CallbackQuery, state: FSMContext):
    uid = callback.from_user.id
    data = await state.get_data()
    save_data(uid, data)    # сохраняем слово и значение во внешний словарь
    await state.set_state(FSMAddWords.word_adding)

    await callback.message.edit_text(
        text=f"{LEXICON_ADD['inv_add_word']}",
        reply_markup=yes_no_kb_markup
    )
    await state.set_state(FSMAddWords.wait_yn_btn_word)


# хендлер обрабатывающий нажатие кнопки "Да" после приглашения добавить новое слово
@router.callback_query(StateFilter(FSMAddWords.wait_yn_btn_word), F.data == 'yes')
async def process_yes_for_add_word(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMAddWords.word_adding)
    await callback.message.edit_text(text=f"{LEXICON_ADD['which_word']}")


# хендлер обрабатывающий ввод чего-либо вместо нажатия кнопок
@router.message(StateFilter(FSMAddWords.wait_yn_btn_mean))
@router.message(StateFilter(FSMAddWords.wait_yn_btn_word))
async def warning_not_press_btns_meaning(message: Message):
    await message.delete()


# хендлер обрабатывающий нажатие кнопки "Нет" после приглашения добавить новое слово
@router.callback_query(StateFilter(FSMAddWords.wait_yn_btn_word), F.data == 'no')
async def process_no_for_add_word(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON['end_of_cicle'])
    await state.clear()


# @router.message(Command(commands='help'))
# async def process_help_command(message: Message):
#     await message.answer(text=LEXICON['/help'])