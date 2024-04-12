from telebot.handler_backends import State, StatesGroup


class RequestState(StatesGroup):
    city = State()
    exact_city = State()
    count_hotels = State()
    photo_output = State()
    request = State()