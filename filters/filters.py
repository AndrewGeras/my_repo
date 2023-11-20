from aiogram.types import Message
from aiogram.filters import BaseFilter
from re import fullmatch


class IsLatinLetters(BaseFilter):
    '''Этот фильтр отбирает тектст написанный латиницей, в котором слова разделены пробелом или тире'''
    async def __call__(self, message: Message) -> bool:
        pattern = r"^[a-zA-Z]+([ -][a-zA-Z]+)*$"
        return message.text and bool(fullmatch(pattern, message.text))


class IsListOfWords(BaseFilter):
    '''этот фильтр определяет является ли введённое сообщение списком слов написанных кириллицей, через запятую'''
    async def __call__(self, message: Message) -> bool:
        pattern = r"^[а-яА-ЯёЁ]+([ ,\-] ?[а-яА-ЯёЁ]+)*$"
        return message.text and bool(fullmatch(pattern, message.text))


class UserAnswer(BaseFilter):
    async def __call__(self, message: Message) -> dict[str, str] | None:
        if message.text:
            return {'user_answer': message.text}


