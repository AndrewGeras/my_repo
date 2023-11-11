from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from utils.utils import load_data, get_dict_page, get_total_pages
from states.states import FSMFindWord, FSMAddWords
from keyboards.keyboards import yes_no_kb_markup
from filters.filters import IsLatinLetters



from lexicon.lexicon import LEXICON_FW, LEXICON, LEXICON_ADD


router = Router()

storage = MemoryStorage()


#  хендлер обрабатывающий ввод комманды "найти значение слова"
@router.message(Command(commands='find_word'), StateFilter(default_state))
async def process_find_word_command(message: Message, state: FSMContext):
    await state.set_data(load_data(message.from_user.id))
    if not await state.get_data():
        await message.answer(text=LEXICON['empty_dict'])
        await state.set_state(FSMAddWords.word_adding)
    else:
        await message.answer(text=f"{LEXICON_FW['which_word']}")
        await state.set_state(FSMFindWord.find_word)
    await message.delete()


#  Хендлер обрабатывающий ввод слова в режиме поиска значения слова
@router.message(StateFilter(FSMFindWord.find_word), IsLatinLetters())
async def process_input_word(message: Message, state: FSMContext):
    data = await state.get_data()
    word = message.text.lower()
    meaning = data.get(word)
    if meaning:
        await message.answer(text=f"<b>{word}</b> - {', '.join(meaning['meaning'])}\n\n")
        await message.answer(
            text=f"Хотите найти другое слово?",
            reply_markup=yes_no_kb_markup
        )
        await state.set_state(FSMFindWord.wait_yn_othr_wrd)
    else:
        await message.answer(
            text=f"<b>{word}</b>{LEXICON_FW['not_found']}",
            reply_markup=yes_no_kb_markup
        )
        await state.set_state(FSMFindWord.wait_yn_ins_wrd)


# хендлер обрабатывающий ввод слова не латиницей в режиме добавления слова в словарь
@router.message(StateFilter(FSMFindWord.find_word), ~IsLatinLetters())
async def warning_nonlating_input(message:Message):
    await message.answer(text=LEXICON_ADD['nonlatin_input'])


#  Хендлер обрабатывающий нажатие кнопки "Да" в предложении найти другое слово
@router.callback_query(StateFilter(FSMFindWord.wait_yn_othr_wrd), F.data == 'yes')
async def process_yes_btn_for_fw(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMFindWord.find_word)
    await callback.message.edit_text(text=f"{LEXICON_FW['which_word']}")


# Хендлер обрабатывающий нажатие кнопки "Да" на предложение добавить слово из поиска в словарь
@router.callback_query(StateFilter(FSMFindWord.wait_yn_ins_wrd), F.data == 'yes')
async def process_yes_add_word(callback: CallbackQuery, state: FSMContext):
    word = callback.message.text[: -len(LEXICON_FW['not_found'])]
    await state.set_data({'word': word, 'meaning': []})
    await callback.message.edit_text(text=f"{LEXICON_ADD['which_mng']} <b><i>{word}</i></b>?")
    await state.set_state(FSMAddWords.mean_adding)


# # хендлер обрабатывающий нажатие кнопки "Нет" после предложения добавить или найти новое слово
@router.callback_query(StateFilter(FSMFindWord.wait_yn_othr_wrd), F.data == 'no')
@router.callback_query(StateFilter(FSMFindWord.wait_yn_ins_wrd), F.data == 'no')
async def process_no_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=LEXICON['end_of_cicle'])
    await state.clear()


#  Хендлер обрабатывающий ввод чего-либо кроме нажатия инлайн-кнопок в режиме показа словаря
@router.message(StateFilter(FSMFindWord.wait_yn_othr_wrd))
@router.message(StateFilter(FSMFindWord.wait_yn_ins_wrd))
async def process_input_in_question(message: Message):
    await message.delete()