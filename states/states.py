
from aiogram.fsm.state import State, StatesGroup



class FSMAddWords(StatesGroup):
    word_adding = State()
    wait_yn_btn_word = State()
    mean_adding = State()
    wait_yn_btn_mean = State()


class FSMShowDict(StatesGroup):
    show_dict = State()


class FSMFindWord(StatesGroup):
    find_word = State()
    wait_yn_othr_wrd = State()
    wait_yn_ins_wrd = State()


class FSMTestWords(StatesGroup):
    wait_choose_mthd = State()
    by_word_mthd = State()
    by_mean_mthd = State()
    look_through_res = State()


