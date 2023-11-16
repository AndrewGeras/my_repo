from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from utils.utils import load_data, get_dict_page, get_total_pages
from states.states import FSMShowDict, FSMAddWords
from keyboards.pagination import create_pagen_keyboard
from lexicon.lexicon import LEXICON, LEXICON_BTN




router = Router()
_wpp = 15  # - количество слов на странице (words per page)

storage = MemoryStorage()


# Хендлер обрабатывающий вызов команды "Посмотреть словарь"
@router.message(Command(commands='show_dict'), StateFilter(default_state))
async def process_show_dict_command(message: Message, state: FSMContext):
    await state.set_data(load_data(message.from_user.id))
    if not await state.get_data():
        await message.answer(text=LEXICON['empty_dict'])
        await state.set_state(FSMAddWords.word_adding)
    else:
        data = await state.get_data()
        total = get_total_pages(data=data, wpp=_wpp)
        text = get_dict_page(data, 0, _wpp)
        await message.answer(
            text=text,
            reply_markup=create_pagen_keyboard(
                'prev_btn',
                f'1/{total}',
                'next_btn'
            )
        )
        await state.set_state(FSMShowDict.show_dict)
    await message.delete()


#  Хендлер обрабатывающий нажатие кнопки "Вперёд"
@router.callback_query(StateFilter(FSMShowDict.show_dict), F.data == 'next_btn')
async def process_nxt_btn_press(callback: CallbackQuery, state: FSMContext):
    page = int(callback.message.reply_markup.inline_keyboard[0][1].text.split('/')[0])
    data = await state.get_data()
    total = get_total_pages(data=data, wpp=_wpp)
    if page < total:
        text = get_dict_page(data, page, _wpp)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagen_keyboard(
                'prev_btn',
                f'{page + 1}/{total}',
                'next_btn'
            )
        )
    await callback.answer()

#  Хендлер обрабатывающий нажатие кнопки "Назад"
@router.callback_query(StateFilter(FSMShowDict.show_dict), F.data == 'prev_btn')
async def process_nxt_btn_press(callback: CallbackQuery, state: FSMContext):
    page = int(callback.message.reply_markup.inline_keyboard[0][1].text.split('/')[0])
    data = await state.get_data()
    total = get_total_pages(data=data, wpp=_wpp)
    if page > 1:
        text = get_dict_page(data, page - 2, _wpp)
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagen_keyboard(
                'prev_btn',
                f'{page - 1}/{total}',
                'next_btn'
            )
        )
    await callback.answer()


#  Хендлер срабатывающий на нажатие стоп-кнопки
@router.message(StateFilter(FSMShowDict.show_dict), F.text == LEXICON_BTN['stop_button'])
async def process_stop_btn_press(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['end_of_cicle'])
    await state.clear()
    await message.delete()


#  Хендлер обрабатывающий ввод чего-либо кроме нажатия инлайн-кнопок в режиме показа словаря
@router.message(StateFilter(FSMShowDict.show_dict))
async def process_input_in_pagen(message: Message):
    await message.delete()