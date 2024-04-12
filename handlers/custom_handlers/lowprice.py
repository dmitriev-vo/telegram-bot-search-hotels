from loader import bot
from states.search_options import RequestState
from telebot.types import Message, InputMediaPhoto
from database.history import add_request
import datetime
from requests_api import functions
from keyboards.inline.cities import gen_markup
import sqlite3 as sl
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from loguru import logger


@bot.message_handler(commands=['lowprice'])
@logger.catch
def lowprice(message: Message) -> None:
    """По команде /lowprice запрашивает от пользователя название города,
    меняет состояние на city и фиксирует команду.
    """
    logger.info(f'{message.from_user.username} : start command /lowprice')
    bot.set_state(message.from_user.id, RequestState.city, message.chat.id)
    logger.info(f'{message.from_user.username} : state change to city')
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.username}! "
                     f"Введите город, в котором будем искать.")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'lowprice'
        logger.info(f'{message.from_user.username} : write command to database')


@bot.message_handler(commands=['highprice'])
@logger.catch
def highprice(message: Message) -> None:
    """По команде /highprice запрашивает от пользователя название города,
    меняет состояние на city и фиксирует команду.
    """
    logger.info(f'{message.from_user.username} : start command /highprice')
    bot.set_state(message.from_user.id, RequestState.city, message.chat.id)
    logger.info(f'{message.from_user.username} : state change to city')
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.username}! "
                     f"Введите город, в котором будем искать")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'highprice'
        logger.info(f'{message.from_user.username} : write command to database')


@bot.message_handler(commands=['bestdeal'])
@logger.catch
def bestdeal(message: Message) -> None:
    """По команде /bestdeal запрашивает от пользователя название города,
    меняет состояние на city и фиксирует команду.
    """
    logger.info(f'{message.from_user.username} : start command /highprice')
    bot.set_state(message.from_user.id, RequestState.city, message.chat.id)
    logger.info(f'{message.from_user.username} : state change to city')
    bot.send_message(message.from_user.id,
                     f"Привет, {message.from_user.username}! "
                     f"Введите город, в котором будем искать")
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['command'] = 'bestdeal'
        logger.info(f'{message.from_user.username} : write command to database')


@bot.message_handler(commands=['history'])
@logger.catch
def history(message: Message) -> None:
    """По команде /history бот отправляет историю только тех запросов, которые были сделаны пользователем."""
    logger.info(f'{message.from_user.username} : start command /history')
    bot.set_state(message.from_user.id, RequestState.request, message.chat.id)
    bot.send_message(message.from_user.id, "Вывожу историю поиска...")
    con = sl.connect('history')
    logger.info(f'{message.from_user.username} : connection to database history')
    with con:
        data = con.execute(f"SELECT * FROM history")
        for i_row, row in enumerate(data):
            if row[0] == message.from_user.username:
                text = f"Номер запроса: {i_row + 1}" + f" Команда: {row[1]}" + \
                       f" Дата и время ввода команды: {row[2]}" + f" Найденные отели: {row[7]}"
                bot.send_message(message.from_user.id, text)
    logger.info(f'{message.from_user.username} : output information from history done')


@bot.message_handler(state=RequestState.city)
@logger.catch
def get_city(message: Message) -> None:
    """В состоянии city бот принимает введенное значение и формирует кнопки из названий городов,
    найденных в функции functions.search_cities.
    """
    logger.info(f'{message.from_user.username} : state in city')
    logger.info(f'{message.from_user.username} : send message: ' + message.text)
    global cities
    try:
        global cities
        logger.info(f'{message.from_user.username} : start function search_cities')
        cities = functions.search_cities(message.text)
        if cities:
            bot.send_message(message.from_user.id, "По запросу найдены следующие города.")
            bot.send_message(message.from_user.id,
                             "Выберете точный город из указанного списка:",
                             reply_markup=gen_markup(cities))
        else:
            bot.send_message(message.from_user.id, "Города не найдены. Попробуйте ввести еще раз.")
    except ConnectionError:
        bot.send_message(message.from_user.id,
                         "Не удалось выполнить поиск городов. Попробуйте ввести еще раз.",
                         reply_markup=gen_markup(cities))
        logger.exception('ConnectionError')


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
@logger.catch
def callback_calendar(call):
    """Callback - функция календаря, последовательно формирует выбор года/месяца/дня и фиксирует дату заезда и выезда.
    Выводит из функции, формируя запрос кнопками да/нет для вывода фотографий.
    Если раннее была введена команда /bestdeal, то выводит из функции, меняя состояние на start_cost.
    """
    logger.info(f'{call.from_user.username} : start enter calendar')
    result, key, step = DetailedTelegramCalendar().process(call.data)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        if not result and key:
            bot.edit_message_text(f"Select {LSTEP[step]}",
                                  call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=key)
        elif result:
            if data['date_in'] == '':
                data['date_in'] = result
                logger.info(f'{call.from_user.username} : entry to database date_in')
                bot.set_state(call.from_user.id, RequestState.date_out, call.message.chat.id)
                logger.info(f'{call.from_user.username} : state change to date_out')
                calendar, step = DetailedTelegramCalendar().build()
                bot.edit_message_text(f"Записал дату заезда: {result}. Теперь выберете дату выезда ",
                                      call.message.chat.id,
                                      call.message.message_id)
                bot.send_message(call.from_user.id, f"Select {LSTEP[step]}", reply_markup=calendar)
            elif data['date_out'] == '':
                data['date_out'] = result
                logger.info(f'{call.from_user.username} : entry to database date_out')
                if data['command'] == 'bestdeal':
                    bot.set_state(call.from_user.id, RequestState.start_cost, call.message.chat.id)
                    logger.info(f'{call.from_user.username} : state change to start_cost')
                    bot.edit_message_text(
                        f"Записал дату выезда: {result}. Теперь введите минимальную стоимость отеля в долларах.",
                        call.message.chat.id,
                        call.message.message_id)
                else:
                    bot.set_state(call.from_user.id, RequestState.photo_output, call.message.chat.id)
                    logger.info(f'{call.from_user.username} : state change to photo_out')
                    bot.edit_message_text(
                        f"Записал дату выезда: {result}. Теперь выберете да/нет, если нужно вывести фото",
                        call.message.chat.id,
                        call.message.message_id)
                    bot.send_message(call.from_user.id,
                                     "Вывести фото?",
                                     reply_markup=gen_markup(["Да", "Нет"]))


@logger.catch
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """Общая callback функция, определяет действия в зависимости от нажатой кнопки.
    Если была нажата кнопка города, то выводит из функции меняя состояние на count_hotels.
    Если была нажата кнопка да, то запрашивает кнопками количество фото.
    Если была нажата кнопка нет, то выполняет запросы API, обрабатывает полученные результаты, выводит пользователю и
    записывает в базу данных.
    """
    if call.data in cities:
        bot.set_state(call.from_user.id, RequestState.count_hotels, call.message.chat.id)
        logger.info(f'{call.from_user.username} : state change to count_hotels')
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="Записал город, теперь введите количество отелей для поиска")
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['city'] = call.data
            logger.info(f'{call.from_user.username} : entry city to database')
            # Очистка дат
            data['date_in'] = ''
            data['date_out'] = ''
            logger.info(f'{call.from_user.username} : dates clear')

    elif call.data == 'Да':
        bot.set_state(call.from_user.id, RequestState.photo_count, call.message.chat.id)
        logger.info(f'{call.from_user.username} : state change to photo_count')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Хорошо, теперь введите количество фото")
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['output_photo'] = 'Да'

    elif call.data == 'Нет':
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['output_photo'] = 'Нет'
            data['count_photo'] = 0
            bot.set_state(call.from_user.id, RequestState.request, call.message.chat.id)
            logger.info(f'{call.from_user.username} : state change to request')
            bot.send_message(call.from_user.id, "Начался поиск...")
            try:
                # Старт выполнения запросов API
                logger.info(f'{call.from_user.username} : start requests API')
                coordinates_city = functions.search_city_coordinates(name_city=data["city"])
                logger.info(f'{call.from_user.username} : function search_city_coordinates done')
                # Поиск и сортировка отелей в зависимости от команды
                if data['command'] == 'bestdeal':
                    hotels_in_city = functions.search_hotels_in_city_with_price_and_distance(
                        coordinates=coordinates_city,
                        command=data['command'],
                        date_in=data["date_in"],
                        date_out=data["date_out"],
                        start_cost=data["start_cost"],
                        stop_cost=data["stop_cost"],
                        start_distance=data["start_distance"],
                        stop_distance=data["stop_distance"],
                        count_hotels=int(data["count_hotels"]))
                    logger.info(f'{call.from_user.username} : '
                                f'function search_hotels_in_city_with_price_and_distance done')
                else:
                    hotels_in_city = functions.search_hotels_in_city(coordinates=coordinates_city,
                                                                     command=data['command'],
                                                                     date_in=data["date_in"],
                                                                     date_out=data["date_out"],
                                                                     count_hotels=int(data["count_hotels"]))
                    logger.info(f'{call.from_user.username} : function search_hotels_in_city done')
                details_hotels = functions.find_details_hotel(hotels_in_city)
                logger.info(f'{call.from_user.username} : function find_details_hotel done')
            except ConnectionError:
                logger.error(f'{call.from_user.username} : connection error')
                bot.send_message(call.from_user.id, 'Не удалось выполнить запрос: ошибка соединения. '
                                                    'Попробуйте начать заново.')
                bot.set_state(call.from_user.id, RequestState.city, call.message.chat.id)
                bot.send_message(call.from_user.id, "Введите город, в котором будем искать")
            except KeyError:
                logger.error(f'{call.from_user.username} : key error')
                bot.send_message(call.from_user.id, 'Не удалось выполнить запрос: ошибка в введенном значении. '
                                                    'Попробуйте начать заново.')
                bot.set_state(call.from_user.id, RequestState.city, call.message.chat.id)
                bot.send_message(call.from_user.id, "Введите город, в котором будем искать")

            # Обработка полученных данных
            count_day = str(data['date_out'] - data['date_in'])[0]
            urls_hotels = ''
            if int(data["count_hotels"]) != 0:
                for i_hotel in range(data["count_hotels"]):
                    cost_holiday = round(int(count_day) * hotels_in_city[i_hotel][3], 2)
                    urls_hotels += f'https://www.hotels.com/h{hotels_in_city[i_hotel][1]}.Hotel-Information . ' + \
                                   'Описание: ' + details_hotels[i_hotel][1]
                    text = f'Ссылка на отель: ' \
                           f'https://www.hotels.com/h{hotels_in_city[i_hotel][1]}.Hotel-Information .' \
                           + ' Название отеля: ' + details_hotels[i_hotel][0] + '. ' + 'Описание отеля: ' \
                           + details_hotels[i_hotel][1] + ' ' + 'Адрес отеля: ' + details_hotels[i_hotel][2] \
                           + '. ' + 'Удаленность от центра ' + str(hotels_in_city[i_hotel][2]) + ' милей. ' \
                           + 'Стоимость номеров от ' + str(round(hotels_in_city[i_hotel][3], 2)) + ' долларов. ' \
                           + 'Количество запланированных дней: ' + count_day + '. ' \
                           + 'Стоимость заезда с учетом дат от ' + str(cost_holiday) + ' долларов.'
                    bot.send_message(call.from_user.id, text)
                # Запись в базу данных
                add_request(data_name='history',
                            name_user=call.from_user.username,
                            command=data['command'],
                            date_create=str(datetime.datetime.utcnow()),
                            city=data["city"],
                            count_hostels=data["count_hotels"],
                            output_photo=data["output_photo"],
                            count_photo=data["count_photo"],
                            found_hotels=urls_hotels)
                logger.info(f'{call.from_user.username} : entry request to history done')


@bot.message_handler(state=RequestState.count_hotels)
@logger.catch
def get_count_hotels(message: Message) -> None:
    """В состоянии count_hotels бот фиксирует количество отелей, меняет состояние на date_in и выводит календарь
    с последующим выбором даты заезда.
    """
    logger.info(f'{message.from_user.username} : state in count_hotels')
    logger.info(f'{message.from_user.username} : send message: ' + message.text)
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['count_hotels'] = int(message.text)
        bot.set_state(message.from_user.id,  RequestState.date_in, message.chat.id)
        logger.info(f'{message.from_user.username} : state change to date_in')
        calendar, step = DetailedTelegramCalendar().build()
        bot.send_message(message.chat.id,
                         f"Записал количество отелей, теперь выберете дату заезда")
        bot.send_message(message.chat.id,
                         f"Select {LSTEP[step]}",
                         reply_markup=calendar)
    else:
        bot.send_message(message.from_user.id, "Количество может быть только числом")
        logger.debug(f'{message.from_user.username} : entered not a number in count_hotels')


@bot.message_handler(state=RequestState.start_cost)
@logger.catch
def get_output_photo(message: Message) -> None:
    """В состоянии start_cost бот фиксирует минимальную стоимость, меняет состояние на stop_cost и
    запрашивает максимальную стоимость.
    """
    logger.info(f'{message.from_user.username} : state in start_cost')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            bot.set_state(message.from_user.id, RequestState.stop_cost, message.chat.id)
            logger.info(f'{message.from_user.username} : state change to stop_cost')
            data['start_cost'] = int(message.text)
            bot.send_message(message.from_user.id, 'Записал минимальную стоимость отеля. '
                                                   'Теперь введите максимальную стоимость отеля в долларах.')
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Значение должно быть числом. Попробуйте еще раз.')
            logger.debug(f'{message.from_user.username} : entered not a number in start_cost')


@bot.message_handler(state=RequestState.stop_cost)
@logger.catch
def get_output_photo(message: Message) -> None:
    """В состоянии stop_cost бот фиксирует максимальную стоимость, меняет состояние на start_distance и
    запрашивает минимальное расстояние до центра города.
    """
    logger.info(f'{message.from_user.username} : state in stop_cost')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            bot.set_state(message.from_user.id, RequestState.start_distance, message.chat.id)
            logger.info(f'{message.from_user.username} : state change to start_distance')
            data['stop_cost'] = int(message.text)
            bot.send_message(message.from_user.id, 'Записал максимальную стоимость отеля. '
                                                   'Теперь введите минимальное расстояние до центра в милях.')
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Значение должно быть числом. Попробуйте еще раз.')
            logger.debug(f'{message.from_user.username} : entered not a number in stop cost')


@bot.message_handler(state=RequestState.start_distance)
@logger.catch
def get_output_photo(message: Message) -> None:
    """В состояние start_distance бот фиксирует минимальное расстояние до города, меняет состояние на stop_distance
    и запрашивает максимальное расстояние до центра города.
    """
    logger.info(f'{message.from_user.username} : state in start_distance')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            bot.set_state(message.from_user.id, RequestState.stop_distance, message.chat.id)
            logger.info(f'{message.from_user.username} : state change to stop_distance')
            data['start_distance'] = int(message.text)
            bot.send_message(message.from_user.id, 'Записал минимальное расстояние до центра. '
                                                   'Теперь введите максимальное расстояние до центра в милях.')
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Значение должно быть числом. Попробуйте еще раз.')
            logger.debug(f'{message.from_user.username} : entered not a number in start_distance')


@bot.message_handler(state=RequestState.stop_distance)
@logger.catch
def get_output_photo(message: Message) -> None:
    """В состоянии stop_distance бот фиксирует максимальное расстояние до центра города, меняет сотояние на
    photo_output и запрашивает кнопками да/нет необходимость вывода фотографий.
    """
    logger.info(f'{message.from_user.username} : state in stop_distance')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            bot.set_state(message.from_user.id, RequestState.photo_output, message.chat.id)
            logger.info(f'{message.from_user.username} : state change to photo_output')
            data['stop_distance'] = int(message.text)
            bot.send_message(message.from_user.id, 'Записал максимальное расстояние до центра.'
                                                   'Теперь выберете да/нет, если нужно вывести фото.')
            bot.send_message(message.from_user.id,
                             "Вывести фото?",
                             reply_markup=gen_markup(["Да", "Нет"]))
        except ValueError:
            bot.send_message(message.from_user.id,
                             'Значение должно быть числом. Попробуйте еще раз.')
            logger.debug(f'{message.from_user.username} : entered not a number in stop_distance')



@bot.message_handler(state=RequestState.photo_count)
@logger.catch
def get_output_photo(message: Message) -> None:
    """В крайнем состоянии photo_count бот фиксирует количество фотографий, выполняет запросы API,
    обрабатывает полученный результат, отправляет пользователю данные с фотографиями и записывает результат
    в базу данных.
    """
    logger.info(f'{message.from_user.username} : state in photo_count')
    bot.set_state(message.from_user.id,  RequestState.request, message.chat.id)
    logger.info(f'{message.from_user.username} : state change to request')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = int(message.text)
        bot.send_message(message.from_user.id, 'Начался поиск...')
        logger.info(f'{message.from_user.username} : start requests API')
        logger.info(f'{message.from_user.username} : start function search_city_coordinates ' + \
                    'parameters: ' + data["city"])
        coordinates_city = functions.search_city_coordinates(data["city"])
        try:
            # Поиск и сортировка отелей в зависимости от команды
            if data['command'] == 'bestdeal':
                logger.info(f'{message.from_user.username} : '
                            f'start function search_hotels_in_city_with_price_and_distance')
                hotels_in_city = functions.search_hotels_in_city_with_price_and_distance(
                    coordinates=coordinates_city,
                    command=data['command'],
                    date_in=data["date_in"],
                    date_out=data["date_out"],
                    start_cost=data["start_cost"],
                    stop_cost=data["stop_cost"],
                    start_distance=data["start_distance"],
                    stop_distance=data["stop_distance"],
                    count_hotels=int(data["count_hotels"]))
            else:
                logger.info(f'{message.from_user.username} : start function search_hotels_in_city')
                hotels_in_city = functions.search_hotels_in_city(coordinates=coordinates_city,
                                                                 command=data['command'],
                                                                 date_in=data["date_in"],
                                                                 date_out=data["date_out"],
                                                                 count_hotels=int(data["count_hotels"]))
            logger.info(f'{message.from_user.username} : start function find_details_hotel')
            details_hotels = functions.find_details_hotel(hotels_in_city)
            logger.info(f'{message.from_user.username} : start function find_photo')
            url_images_hotels = functions.find_photo(hotels_in_city, int(data["count_photo"]))
            count_day = str(data['date_out'] - data['date_in'])[0]
        except ConnectionError:
            logger.error(f'{message.from_user.username} : ConnectionError')
            bot.send_message(message.from_user.id, 'Не удалось выполнить запрос: ошибка соединения.'
                                                   'Попробуйте начать заново.')
            bot.set_state(message.from_user.id, RequestState.city, message.chat.id)
            bot.send_message(message.from_user.id, "Введите город, в котором будем искать")
        except KeyError:
            logger.error(f'{message.from_user.username} : KeyError')
            bot.send_message(message.from_user.id, 'Не удалось выполнить запрос: ошибка в значении.'
                                                   'Попробуйте начать заново.')
            bot.set_state(message.from_user.id, RequestState.city, message.chat.id)
            bot.send_message(message.from_user.id, "Введите город, в котором будем искать")
        logger.info(f'{message.from_user.username} : requests API done')
        # Вывод информации об отеле и фотографии
        logger.info(f'{message.from_user.username} : start information output')
        if int(data["count_hotels"]) != 0:
            bot.send_message(message.from_user.id, 'Вот, что я нашел!')
            urls_hotels = ''

            for i_hotel in range(data["count_hotels"]):
                cost_holiday = round(int(count_day) * hotels_in_city[i_hotel][3], 2)
                urls_hotels += f'https://www.hotels.com/h{hotels_in_city[i_hotel][1]}.Hotel-Information . ' + \
                               'Описание: ' + details_hotels[i_hotel][1]
                text = f'Ссылка на отель: https://www.hotels.com/h{hotels_in_city[i_hotel][1]}.Hotel-Information . ' \
                       + 'Название отеля: ' + details_hotels[i_hotel][0] + '. ' + 'Описание отеля: ' \
                       + details_hotels[i_hotel][1] + ' ' + 'Адрес отеля: ' + details_hotels[i_hotel][2] \
                       + '. ' + 'Удаленность от центра ' + str(hotels_in_city[i_hotel][2]) + ' милей. ' \
                       + 'Стоимость номеров от ' + str(round(hotels_in_city[i_hotel][3], 2)) + ' долларов. ' \
                       + 'Количество запланированных дней: ' + count_day + '. ' + 'Стоимость заезда с учетом дат от ' \
                       + str(cost_holiday) + ' долларов.'
                bot.send_message(message.from_user.id, text)
                photos_hotel = url_images_hotels.__next__()
                media = [InputMediaPhoto(url, caption=text) for url in photos_hotel]
                bot.send_media_group(chat_id=message.chat.id, media=media)
        logger.info(f'{message.from_user.username} : information output done')
        # Запись в базу данных
        logger.info(f'{message.from_user.username} : start function add_request in history')
        add_request(data_name='history',
                    name_user=message.from_user.username,
                    command=data['command'],
                    date_create=str(datetime.datetime.utcnow()),
                    city=data["city"],
                    count_hostels=data["count_hotels"],
                    output_photo=data["output_photo"],
                    count_photo=data["count_photo"],
                    found_hotels=urls_hotels)
        logger.info(f'{message.from_user.username} : request done')


logger.add('logs/logs.log', format='{time}; {level}; {message}')
