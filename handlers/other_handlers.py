from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from lexicon.lexicon import LEXICON, LEXICON_BTN


router = Router()


#  Хендлер срабатывающий на нажатие стоп-кнопки
@router.message(F.text == LEXICON_BTN['stop_button'], ~StateFilter(default_state))
async def process_stop_btn_press(message: Message, state: FSMContext):
    await message.answer(text=LEXICON['end_of_cicle'])
    await state.clear()
    await message.delete()


# Хендлер обрабатывает нажатие стоп-кнопки вне какого-либо режима
@router.message(F.text == LEXICON_BTN['stop_button'], StateFilter(default_state))
async def process_idler_stop_btn(message: Message):
    await message.answer(text=LEXICON['idler_stop_button'])
    await message.delete()

