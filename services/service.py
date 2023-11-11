from dataclasses import dataclass
import json


@dataclass
class DictItem:
    key: str   #  само слово (первичный ключ)
    meaning: list[str]  #  список его значений
    u_answ: str = None  #  последний ответ пользователя
    t_status: str = None    #  статус для режима проверки слов (test-status)
    m_status: bool = None   #  статус запомненности (memorization-status)

    def __str__(self):
        return f"{self.key} - {', '.join(self.meaning)}. TS: {self.t_status}, MS: {self.m_status}"

    def to_dict(self):
        return {
            self.key: {
                'meaning': self.meaning,
                'u_answ': self.u_answ,
                't_status': self.t_status,
                'm-status': self.m_status
            }
        }


class DataBase:
    def __init__(self, data: dict[str, dict[str, list[str] | str]]):
        self.data = (DictItem(
            key=key,
            meaning=data[key]['meaning'],
            u_answ=data[key]['u_answ'],
            t_status=data[key]['t_status'],
            m_status=int(data[key]['m-status'])
        ) for key in data)
