from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from lexicon.lexicon import LEXICON, LEXICON_BTN, LEXICON_COMMANDS
from users_data.users import check_user_in_list, add_user_to_list
from keyboards.keyboards import stop_keyboard
from json import dump


router = Router()


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


# Хендлер обрабатывает нажатие стоп-кнопки вне какого-либо режима
@router.message(F.text == LEXICON_BTN['stop_button'], StateFilter(default_state))
async def process_idler_stop_btn(message: Message):
    await message.answer(text=LEXICON['idler_stop_button'])
    await message.delete()


# Хендлер обрабатывает отправку любого сообщения вне какого-либо режима
@router.message(StateFilter(default_state), ~F.text.in_(LEXICON_COMMANDS.keys()))
async def process_idler_update(message: Message):
    await message.delete()
