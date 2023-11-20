from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext


from lexicon.lexicon import LEXICON, LEXICON_TEST, LEXICON_ADD, LEXICON_BTN
from states.states import FSMTestWords, FSMAddWords
from keyboards.keyboards import word_mean_kb_markup, yes_no_kb_markup, stop_keyboard
from utils.utils import (load_data, proc_user_resp, choice_next_word, save_result,
                         choise_first_word, get_wt_result, get_mt_result, t_status_to_none)



router = Router()


#  Хендлер обрабатывающий команду "Проверить знание слов"
@router.message(Command(commands='test'), StateFilter(default_state))
async def process_test_command(message: Message, state: FSMContext):
    await state.set_data(load_data(message.from_user.id))
    if await state.get_data():
        await message.answer(
            text='Как будем проверять?',
            reply_markup=word_mean_kb_markup
        )
        await state.set_state(FSMTestWords.wait_choose_mthd)
    else:
        await message.answer(text=LEXICON['empty_dict'])
        await state.set_state(FSMAddWords.word_adding)

    await message.delete()


#  Хендлер обрабатывающий нажатие кнопки "По словам"
@router.callback_query(StateFilter(FSMTestWords.wait_choose_mthd), F.data == 'by_word')
async def process_by_word_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMTestWords.by_word_mthd)
    data = await state.get_data()
    text, data, finished = choise_first_word(data)
    if finished:
        await state.clear()
        await callback.message.edit_text(
            text=text,
            reply_markup=yes_no_kb_markup
        )
        await state.set_state(FSMAddWords.wait_yn_btn_word)
    else:
        await state.update_data(data)
        await callback.message.edit_text(text=text)


#  Хендлер обрабатывающий нажатие кнопки "По значениям"
@router.callback_query(StateFilter(FSMTestWords.wait_choose_mthd), F.data == 'by_meaning')
async def process_by_mean_btn(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMTestWords.by_mean_mthd)
    data = await state.get_data()
    text, data, finished = choise_first_word(data)
    if finished:
        await state.clear()
        await callback.message.edit_text(
            text=text,
            reply_markup=yes_no_kb_markup
        )
        await state.set_state(FSMAddWords.wait_yn_btn_word)
    else:
        await state.update_data(data)
        await callback.message.edit_text(text=', '.join(data[text]['meaning']))


# Хендлер обрабатывающий нажатие стоп-кнопки во время теста по словам
@router.message(StateFilter(FSMTestWords.by_word_mthd), F.text == LEXICON_BTN['stop_button'])
async def process_stop_btn_in_word_test(message: Message, state: FSMContext):
    data = await state.get_data()
    text = get_wt_result(data)
    await message.answer(text=text)
    data = t_status_to_none(data)
    save_result(message.from_user.id, data)
    await state.clear()
    await message.delete()


# Хендлер обрабатывающий нажатие стоп-кнопки во время теста по значениям
@router.message(StateFilter(FSMTestWords.by_mean_mthd), F.text == LEXICON_BTN['stop_button'])
async def process_stop_btn_in_word_test(message: Message, state: FSMContext):
    data = await state.get_data()
    text = get_mt_result(data)
    await message.answer(text=text)
    data = t_status_to_none(data)
    save_result(message.from_user.id, data)
    await state.clear()
    await message.delete()


#  Хендлер обраатывающий ввод слова в методе проверки "по словам"
@router.message(StateFilter(FSMTestWords.by_word_mthd), F.text, ~F.text.startswith('/'))
async def process_user_meaning(message: Message, state: FSMContext):
    text, data = proc_user_resp(await state.get_data(), message.text.lower(), method='by_word')
    await message.answer(text=text)

    #  отбираем слово из неопрошенных и если таких больше нет выдаём резульат теста
    text, data, finished = choice_next_word(data, method='by_word')
    await message.answer(text=text)
    await state.update_data(data)
    if finished:
        save_result(message.from_user.id, data)
        await state.clear()


#  Хендлер обрабатывающий ввод слова при методе проверки "по значениям"
@router.message(StateFilter(FSMTestWords.by_mean_mthd), F.text, ~F.text.startswith('/'))
async def process_user_word(message: Message, state: FSMContext):
    data = await state.get_data()
    text, data = proc_user_resp(data, message.text.lower(), method='by_meaning')
    await message.answer(text=text)

    #  отбираем слово из неопрошенных и если таких больше нет выдаём резульат теста
    text, data, finished = choice_next_word(data, method='by_meaning')
    await message.answer(text=text)
    await state.update_data(data)
    if finished:
        save_result(message.from_user.id, data)
        await state.clear()


#Хендлер обрабатывающий отправку потенциальной команды
@router.message(StateFilter(FSMTestWords.by_word_mthd), F.text, F.text.startswith('/'))
@router.message(StateFilter(FSMTestWords.by_mean_mthd), F.text, F.text.startswith('/'))
async def warning_some_command_input(message: Message):
    await message.delete()


# Хендлер обрабатывающий отправку пользователем нетекстопого сообщения
@router.message(StateFilter(FSMTestWords.by_word_mthd), ~F.text)
@router.message(StateFilter(FSMTestWords.by_mean_mthd), ~F.text)
async def process_nontext_update(message: Message):
    await message.delete()


# хендлер обрабатывающий ввод чего-либо вместо нажатия кнопок
@router.message(StateFilter(FSMTestWords.wait_choose_mthd))
async def process_not_press_btns(message: Message):
    await message.delete()