from aiogram.types import Message
from aiogram.filters import BaseFilter
from string import ascii_letters
from re import fullmatch


class IsLatinLetters(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text and all((i in (ascii_letters + ' ') for i in message.text))


class IsListOfWords(BaseFilter):
    '''этот фильтр определяет является ли введённое сообщение списком слов написанных кириллицей, через запятую'''
    async def __call__(self, message: Message) -> bool:
        pattern = r"^ *((([а-яА-Я])+|([а-яА-Я])+[ \-]([а-яА-Я])+) *, *)*(([а-яА-Я])+|([а-яА-Я])+[ \-]([а-яА-Я])+) *$"
        return message.text and bool(fullmatch(pattern, message.text))


class UserAnswer(BaseFilter):
    async def __call__(self, message: Message) -> dict[str, str] | None:
        if message.text:
            return {'user_answer': message.text}


