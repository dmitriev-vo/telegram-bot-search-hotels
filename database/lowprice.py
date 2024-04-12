import sqlite3 as sl


def create_table_users(name_data: str) -> None:
    con = sl.connect(name_data)
    with con:
        data = con.execute("select count(*) from sqlite_master where type='table' and name='lowprice'")
        for row in data:
            if row[0] == 0:
                with con:
                    con.execute("""
                        CREATE TABLE lowprice (
                            name_user VARCHAR,
                            data_create VARCHAR,
                            city VARCHAR,
                            count_hostels VARCHAR,
                            output_photo VARCHAR);
                        """)


def add_lowprice_request(data_name: str, name_user: str, date_create: str, city: str, count_hostels: str, output_photo: str) -> None:
    con = sl.connect(data_name)
    sql = 'INSERT INTO lowprice (name_user, data_create, city, count_hostels, output_photo) values(?, ?, ?, ?, ?)'
    with con:
        con.executemany(sql, [(name_user, date_create, city, count_hostels, output_photo)])


def check_table(data_name, name_table):
    con = sl.connect(data_name)
    with con:
        data = con.execute(f"SELECT * FROM {name_table}")
        for row in data:
            print(row)


data_name = 'history'
create_table_users(data_name)
