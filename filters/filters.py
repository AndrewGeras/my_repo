from aiogram.types import Message
from aiogram.filters import BaseFilter
from string import ascii_letters



class IsLatinLetters(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.text and all((i in (ascii_letters + ' ') for i in message.text))


class UserAnswer(BaseFilter):
    async def __call__(self, message: Message) -> dict[str, str] | None:
        if message.text:
            return {'user_answer': message.text}

