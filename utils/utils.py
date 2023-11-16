from json import load, dump
from services.service import DictItem
from random import choice
from lexicon.lexicon import LEXICON_TEST, LEXICON


def load_data(uid: int) -> dict[str, list[str]]:
    with open(f'users_data/vocabularies/{uid}.json', encoding='utf-8') as file:
        temp_dict = load(file)
    return temp_dict


def save_data(uid: int, data: dict[str, list[str]]) -> None:
    temp_dict = load_data(uid)
    word, meaning = data['word'], data['meaning']
    temp_dict.update(DictItem(word, meaning).to_dict())
    with open(f'users_data/vocabularies/{uid}.json', 'w', encoding='utf-8') as file:
        dump(temp_dict, file, ensure_ascii=False, indent=2)


def word_in_data(uid: int, word: str) -> list[str] | None:
    temp_dict = load_data(uid)
    value = temp_dict.get(word)
    return value['meaning'] if value else None



def get_dict_page(data: dict[str, dict[str, list[str] | str | int]], page: int, wpp: int) -> str:
    # wpp - количетсво слов на одной странице (words per page)
    text = '\n\n'.join(tuple(f'{LEXICON["mark"][data[word]["m_status"]]}{n}. '
                             f'<b>{word}</b> - {", ".join(data[word]["meaning"])}' for n, word in
                             enumerate(tuple(data.keys())[page * wpp: (page + 1) * wpp], wpp * page + 1)))
    return text


def get_total_pages(data: dict[str, list[str]], wpp: int) -> int:
    return len(data) // wpp + (0, 1)[bool(len(data) % wpp)]


def get_wt_result(data: dict[str, dict[str, list[str] | str | int | None]]) -> str:
    return '\n\n'.join(
        (f"{n}. <b>{word}</b> - {', '.join(data[word]['meaning'])}\n"
         f"\t<i>Ваш ответ:  <u>{data[word]['u_answ']}</u></i> {('❌', '✅')[data[word]['u_answ'] in data[word]['meaning']]}"
         for n, word in enumerate(data, 1))) + \
           f"\n\n<b>Ваш результат: {sum(data[word]['u_answ'] in data[word]['meaning'] for word in data)} из {len(data)}</b>"


def get_mt_result(data: dict[str, dict[str, list[str] | str | int | None]]) -> str:
    return '\n\n'.join(
        (f"{n}. {', '.join(data[word]['meaning'])} - <b>{word}</b>\n"
         f"\t<i>Ваш ответ:  <u>{data[word]['u_answ']}</u></i> {('❌', '✅')[data[word]['u_answ'] == word]}"
         for n, word in enumerate(data, 1))) + \
           f"\n\n<b>Ваш результат: {sum(data[word]['u_answ'] == word for word in data)} из {len(data)}</b>"


def proc_user_resp(data: dict[str, dict[str, list[str] | str | bool | None]], text: str, method: str) -> tuple[str, dict]:
    '''функция принимает словарь с данными, ответ пользователя и метод тестирования.
    Затем обрабатывает словарь данных и выдаёт ответ верно или нет ответил пользователь'''
    word = tuple(filter(lambda x: data[x]['t_status'] is True, data.keys()))[0]
    data[word]['u_answ'] = text
    data[word]['t_status'] = False

    if method == 'by_word':
        data[word]['m_status'] = data[word]['m_status'] + (data[word]['m_status'] == 0) + (
                    text in data[word]['meaning'])
        response = choice(
            (LEXICON_TEST['wrong_answ'], LEXICON_TEST['right_answ'])
            [text in data[word]['meaning']])

    if method == 'by_meaning':
        data[word]['m_status'] = data[word]['m_status'] + (data[word]['m_status'] == 0) + (text == word)
        response = choice(
            (LEXICON_TEST['wrong_answ'], LEXICON_TEST['right_answ'])
            [text == word])

    return response, data


def t_status_to_none(data: dict[str, dict[str, list[str] | str | bool | None]]) -> dict:
    '''функция приводит все значения t_status к None'''
    for x in filter(lambda x: not x['t_status'] is None, data.values()):
        x['t_status'] = x['u_answ'] = None
    return data


def choise_first_word(data: dict) -> tuple:
    '''Функция отбирает и возвращает слово из незапомненных
    или возвращает ответ, что незапомненных слов нет'''
    words = tuple(filter(lambda x: data[x]['m_status'] < 3, data))
    if words:
        word = choice(words)
        data[word]['t_status'] = True
        return word, data, False
    return LEXICON_TEST['is_all_memorized'], data, True


def choice_next_word(data: dict[str, dict[str, list[str] | str | bool | None]], method: str) -> tuple[str, dict, bool]:
    '''функци принимает словарь с данными и метод тестирования.
    Выбирает слово из неопрошенных и возвращает его.
    А если таких не осталось возвращает результат тестирования'''
    words = tuple(filter(lambda x: data[x]['t_status'] is None and data[x]['m_status'] < 3, data.keys()))
    if words:
        word = choice(words)
        data[word]['t_status'] = True
        text = word if method == 'by_word' else ', '.join(data[word]['meaning'])
        return text, data, False
    text = get_wt_result(data) if method == 'by_word' else get_mt_result(data)
    t_status_to_none(data)
    return text, data, True


def save_result(uid: int, data: dict):
    with open(f'users_data/vocabularies/{uid}.json', 'w', encoding='utf-8') as file:
        dump(data, file, ensure_ascii=False, indent=2)