import sqlite3 as sl


def create_table_users(name_data: str) -> None:
    """Создает таблицу history с полями.

    Формируемые поля:
    name_user: str - имя пользователя
    command: str - введенная команда
    data_create: str - дата создания строки
    city: str - город поиска
    count_hostels: str - количество отелей
    output_photo: str - необходимость вывода фотографий
    count_photo: str - количество фотографий
    fount_hotels: str - найденные отели

    :return
    None
    """
    con = sl.connect(name_data)
    with con:
        data = con.execute("select count(*) from sqlite_master where type='table' and name='history'")
        for row in data:
            if row[0] == 0:
                with con:
                    con.execute("""
                        CREATE TABLE history (
                            name_user VARCHAR,
                            command VARCHAR,
                            data_create VARCHAR,
                            city VARCHAR,
                            count_hostels VARCHAR,
                            output_photo VARCHAR,
                            count_photo VARCHAR,
                            found_hotels VARCHAR);
                        """)


def add_request(data_name: str, command: str, name_user: str, date_create: str, city: str,
                count_hostels: str, output_photo: str, count_photo: str = '0', found_hotels: str = '') -> None:
    """Формирует строку из параметров и записывает в таблицу data_name.

    :parameters:
    data_name: str -> название файла данных
    command: str -> введенная команда
    name_user: str -> имя пользователя
    date_create: str -> дата создания запроса
    city: str -> название города
    count_hostels: str -> количество отелей
    output_photo: str -> необходимость вывода фотографий
    found_hotels: str -> найденные отели

    :return
    None
    """
    con = sl.connect(data_name)
    sql = 'INSERT INTO history (name_user, command, data_create, city,' \
          'count_hostels, output_photo, count_photo, found_hotels) ' \
          'values(?, ?, ?, ?, ?, ?, ?, ?)'
    with con:
        con.executemany(sql, [(name_user, command, date_create, city, count_hostels,
                               output_photo, count_photo, found_hotels)])


data_name = 'history'
create_table_users(data_name)
