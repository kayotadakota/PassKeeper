import psycopg2
from sys import exit
from os import environ
from psycopg2 import connect


secrets = {
    'dbname': environ['dbname'],
    'user': environ['user'],
    'password': environ['password'],
    'host': environ['host'],
    'port': environ['port']
}


class Transaction():
    def __init__(self, **kwargs):
        self._conn = connect(**kwargs)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params)

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.fetchall()

    def list_data(self):
        return self.query('SELECT * FROM creds;')

    def add_new_data(self, *data):
        sql = 'INSERT INTO creds (url, login, password)'
        sql += 'VALUES (%s, %s, %s)'
        self.execute(sql, *data)

    def delete_data(self, url_name):
        sql = f"DELETE FROM creds WHERE url = '{url_name}'"
        self.execute(sql)

    def search_data(self, url_name):
        sql = "SELECT login, password FROM creds "
        sql += f"WHERE url LIKE '{url_name}%';"
        return self.query(sql)


print()
print('Connected to the PostgreSQL database')
print()


operations = {
    1: 'List data',
    2: 'Search data',
    3: 'Add new data',
    4: 'Delete data',
    5: 'Exit'
}

while True:
    with Transaction(**secrets) as flow:
        for num, oper in operations.items():
            print(num, oper)

        print()
        select = int(input('Choose a number: '))
        print()

        if select == 5:
            exit()

        elif select == 1:
            for row in flow.list_data():
                print(f'Url: "{row[1]}", Login: "{row[2]}", Password: "{row[3]}"')

        elif select == 2:
            url = input('Type partial url for search: ')
            result = flow.search_data(url)
            if not result:
                print('There is no matching data')
            else:
                for row in result:
                    print(f'Login: "{row[0]}", Password: "{row[1]}"')

        elif select == 3:
            url = input('Url: ')
            login = input('Login: ')
            password = input('Password: ')

            try:
                flow.add_new_data((url, login, password))
            except (Exception, psycopg2.DatabaseError) as error:
                print()
                print('Specified url already exists')
                print()

        elif select == 4:
            url = input('Type url of deleting object: ')
            flow.delete_data(url)
            print()
