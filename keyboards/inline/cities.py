from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def gen_markup(cities: List):
    """Формирует кнопки из списка городов.

    :parameter
    cities: List = ['name_city', 'name_city']

    :return
    markup: class 'telebot.types.InlineKeyboardMarkup'
    """
    markup = InlineKeyboardMarkup()
    markup.row_width = len(cities)
    for i_city in cities:
        markup.add((InlineKeyboardButton(i_city, callback_data=i_city)))
    return markup
