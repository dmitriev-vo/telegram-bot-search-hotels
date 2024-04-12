from telebot.handler_backends import State, StatesGroup


class RequestState(StatesGroup):

    """
    Класс состояний для бота.
    ...
    Атрибуты
    --------
    city : class
        название города
    count_hotels : class
        количество отелей
    date_in : class
        дата заезда в отель
    date_out : class
        дата выезда из отеля
    start_cost : class
        начальная цена отеля
    stop_cost : class
        конечная цена отеля
    start_distance : class
        минимальное расстояние до центра города
    photo_output : str
        необходимость вывода фотографий
    photo_count : class
        количество фотографий
    request : class
        состояние выполненного запроса
    """

    city = State()
    count_hotels = State()
    date_in = State()
    date_out = State()
    start_cost = State()
    stop_cost = State()
    start_distance = State()
    stop_distance = State()
    photo_output = State()
    photo_count = State
    request = State()
