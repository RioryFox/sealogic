import sqlite3
import pandas as pd
import time

def new_in_sql():
    try:
        os.remove('ninfo.db')
    except Exception:
        print('Записывающей бд не сущестовало, создаю новую')
    try:
        sheet_name = 'Rates'
        df = pd.read_excel('bd.xlsx', sheet_name=sheet_name, skiprows=1)
        use = ''
        name_value = ''
        query = ''
        for index, row in df.iterrows():
            use = row.tolist()
            query = 'CREATE TABLE IF NOT EXISTS info('
            break
        with sqlite3.connect('ninfo.db') as db:
            cursor = db.cursor()
            for i in range(0, len(use)):
                t = use[i]
                t = str(t)
                t = t.replace(' ', '')
                t = t.replace('-', '')
                t = t.replace('/', '')
                t = t.lower()
                if i != len(use)-1:
                    query += f'{t} TEXT, '
                    name_value += f'{t}, '
                else:
                    query += f'{t} TEXT);'
                    name_value += f'{t}'
            cursor.executescript(query)
            db.commit()
        try:
            df = pd.read_excel('bd.xlsx', sheet_name=sheet_name, skiprows=2)
        except Exception as error:
            print(f'Таблица не верного формата, такого листа не существует: {error}')
            return 'N'
        for index, row in df.iterrows():
            values = row.tolist()
            ovalues = list(map(str, values))
            values = []
            for elem in ovalues:
                if elem == '':
                    elem = 'None'
                values.append(elem)
            try:
                find = f"INSERT INTO info ({name_value}) VALUES ({'?, '*(len(values)-1)}?)"
                with sqlite3.connect('ninfo.db') as db:
                    cursor = db.cursor()
                    cursor.execute(find, values)
                    cursor.execute(find, values)
                    db.commit()
            except sqlite3.Error as e1:
                print(f"Ошибка при выполнении операции сохранения данных из новой exel в sql: {e1}")
                return 'N'
    except Exception as e:
        print(f"Ошибка при открытии exel что только что был получен для обновления: {e}")
        return 'N'
    try:
        try:
            db.close()
        except Exception:
            with sqlite3.connect('ninfo.db') as db:
                db.close()
    except Exception:
        print('БД уже закрыта')
    try:
        os.remove('info.db')
    except Exception:
        print('БД не существовала')

    time.sleep(12)
    try:
        os.rename('ninfo.db', 'info.db')
        return 'Y'
    except Exception as e:
        print(f'Ошибка при переименовании файла: {e}')
        return 'N'

def reg_amdin(user_id, key=None):
    try:
        find = 'SELECT userid FROM admins WHERE userid = ?'
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute(find, [user_id])
        alpha = str(cursor.fetchone())
        if not (alpha == 'None') and key is None:
            return 'Y'
        elif alpha == 'None' and key is None:
            return 'N'
        elif not (key is None) and alpha == 'None':
            values = [user_id]
            new_find = 'INSERT INTO admins (userid) VALUES (?)'
            cursor.execute(new_find, values)
            db.commit()
        else:
            return 'Y'
    except sqlite3.Error as error:
        print(f'Ошибка reg_admins: {error}')
        return 'error'


import os

def rename_database():
    try:
        with sqlite3.connect('ninfo.db') as db:
            db.close()
    except Exception:
        print('БД уже закрыта')
    try:
        os.remove('info.db')
    except Exception:
        print('БД не существовала')

    time.sleep(12)
    try:
        os.rename('ninfo.db', 'info.db')
        return 'Y'
    except Exception as e:
        print(f'Ошибка rename_database: {e}')
        return 'N'

def creat_excel(many):
    if many == '/all':
        many = ''
        like_how = []
    elif many == '/done':
        many = 'WHERE result = ?'
        like_how = ['Done']
    elif many == '/fail':
        many = 'WHERE result = ?'
        like_how = ['Fail']
    with sqlite3.connect('get.db') as db:
        find = f'SELECT * FROM users {many}'
        cursor = db.cursor()
        cursor.execute(find, like_how)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=['mail' , 'id пользователя', 'pol', 'pod', 'pol_ru', 'pod_ru', 'soc / coc ', 'dem', 'кол-во ящиков', 'итог поиска по критериям', 'время завершения запроса'])
        df.to_excel('output.xlsx', index=False)
    db.commit()
    db.close()

def for_admins(last_time=None):
    with sqlite3.connect('get.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT timestamp FROM users')
        client = cursor.fetchall()
        client = client[len(client)-1][0]
    if last_time is None:
        return client
    with sqlite3.connect('get.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE timestamp = ?', [last_time])
        client = cursor.fetchone()
    with sqlite3.connect('users.db') as db:
        cursor = db.cursor()
        cursor.execute('SELECT userid FROM admins')
        admins = cursor.fetchall()
    result = client[9]
    if result != 'Fail':
        return client, admins
    else:
        return client, None
