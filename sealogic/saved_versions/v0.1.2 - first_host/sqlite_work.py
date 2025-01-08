import sqlite3
import pandas as pd
import os
import Levenshtein

def creat_tables():
    with sqlite3.connect("users.db") as db:
        cursor = db.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS users(
        userid INTEGER, 
        mail TEXT
        );
        CREATE TABLE IF NOT EXISTS admins(
        userid INTEGER
        );"""
        cursor.executescript(query)
    ####userid - id пользователя, mail - почта (работоспособная только), key_auth - код, который отправлялся на почту для проверки работоспособности почты, approved - допущен ли пользователь('y'/'n')
    ####userid - id администратора, key - ключ-приглашение для участия в администрировании бота (данный администратор сможет вносить новую информацию в бота лично), approved - допущен ли администратор('y'/'n')

    with sqlite3.connect("get.db") as db:
        cursor = db.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS users(
        mail TEXT,
        userid TEXT,
        pol TEXT,
        pod TEXT,
        pol_ru TEXT,
        pod_ru TEXT,
        soccoc TEXT,
        dem TEXT,
        many TEXT,
        result TEXT,
        Timestamp DATE DEFAULT (datetime('now','localtime'))
        );
        """
        cursor.executescript(query)

def reg_user(user_id, mail=None):
    ####Что бы не награмождать тут сложности я сделаю что эта функция только встречает пользователя и регистрирует его
    try:
        find = 'SELECT mail FROM users WHERE userid = ?'
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute(find, [user_id])
        alpha = str(cursor.fetchone())
        if alpha == 'None' and not (mail is None):
            find = 'SELECT userid FROM users WHERE mail = ?'
            cursor.execute(find, [mail])
            alpha = str(cursor.fetchone())
            if alpha == 'None':
                values = [user_id, mail]
                new_find = 'INSERT INTO users (userid, mail) VALUES (?, ?)'
                cursor.execute(new_find, values)
                db.commit()
                return 'done'
        elif alpha == 'None' and mail is None:
            return alpha
    except sqlite3.Error as e1:
        print(f"fail registration user - {e1}")
        return 'error'
    return 'Y'


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
    except sqlite3.Error as e1:
        print(f"fail refistration admin - {e1}")
        return 'error'
    return 'Y'


def get_list(if_admin=None):
    try:
        if if_admin is None:
            find = 'SELECT userid FROM users'
        else:
            find = 'SELECT userid FROM admins'
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute(find, [])
        alpha = str(cursor.fetchall())
        return alpha
    except sqlite3.Error as e1:
        print(e1)
        return 'error'

def new_in_sql():
    if os.path.exists('ninfo.db'):
        try:
            os.remove('ninfo.db')
        except Exception:
            print("error with delete file ninfo.db")
    try:
        sheet_name = 'Rates'
        df = pd.read_excel('bd.xlsx', sheet_name=sheet_name, skiprows=1)
        use = ''
        name_value = ''
        query = ''
        for index, row in df.iterrows():
            use = row.tolist()
            query = 'CREATE TABLE IF NOT EXISTS ninfo('
            break
        with sqlite3.connect('ninfo.db') as db:
            db = sqlite3.connect('ninfo.db')
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
        df = pd.read_excel('bd.xlsx', sheet_name=sheet_name, skiprows=2)
        for index, row in df.iterrows():
            values = row.tolist()
            values = list(map(str, values))
            try:
                find = f"INSERT INTO ninfo ({name_value}) VALUES ({'?, '*(len(values)-1)}?)"
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
    if os.path.exists('info.db'):
        try:
            os.remove('info.db')
            os.rename('ninfo.db', 'info.db')
            os.remove('ninfo.db')
        except Exception:
            os.rename('ninfo.db', 'info.db')
            print('БД не существовало, генерирую новую')
    return 'Y'



short_list = 'Company	line	last update	POL	Mode1	T/S port	Mode2	POD	Drop off	POL_ru	COL	POD_ru	COD	bonded / non-bonded	Import / Export	Valid till	service	Transit time	Rate Type	SOC / COC	Dem	Many	Tare type	IMO	Rate	Carrency	Полная ставка	Изменение	Актуальность	Акт	Тип перевозки	Frequency'.split('	')


def shablon(user_id):
    lol = {'user_id': user_id,
           'POL': None,
           'POD': None,
           'POL_ru': None,
           'POD_ru': None,
           'SOC / COC': None,
           'Dem': None,
           'many': None,
           'Result': None
           }
    return lol

def sql_get_result(listick):
    find = 'SELECT Rate, Carrency FROM info WHERE '
    finder = []
    for element in listick:
        elem = listick[element]
        elem = str(elem)
        if not(elem.isdigit() or elem == 'None') and not(element == 'many' or element == 'user_id' or element == 'Result'):
            element = element.replace(' ', '')
            element = element.replace('-', '')
            element = element.replace('/', '')
            element = element.lower()
            finder.append(elem)
            find += f'{element} = ? AND '
    try:
        find = find[:len(find)-4]
        db = sqlite3.connect('info.db')
        cursor = db.cursor()
        cursor.execute(find, finder)
        alpha = cursor.fetchall()
        if len(alpha) > 0:
            return alpha
        else:
            return 'N'
    except Exception as error:
        print(f'Ошибка sql_get_result: {error}')

def sql_get(what, where):
    find = f'SELECT * FROM info WHERE {where} = ?'
    try:
        db = sqlite3.connect('info.db')
        cursor = db.cursor()
        cursor.execute(find, [what])
        alpha = cursor.fetchall()
        if len(alpha) == 0:
            return 'N'
        else:
            return alpha
    except Exception as error:
        print(f'Ошибка sql_get: {error}')

def save_result(history):
    try:
        user_id = history['user_id']
        with sqlite3.connect('users.db') as db:
            find = 'SELECT mail FROM users WHERE userid = ?'
            cursor = db.cursor()
            cursor.execute(find, [user_id])
            mail = cursor.fetchone()[0]

        lol = [mail]
        history = history.values()
        for elem in history:
            lol.append(elem)
        lol = list(map(str, lol))

        with sqlite3.connect('get.db') as db:
            find = 'INSERT INTO users (mail, userid, pol, pod, pol_ru, pod_ru, soccoc, dem, many, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
            cursor = db.cursor()
            cursor.execute(find, lol)
        db.commit()
        db.close()
    except Exception as error:
        print(f'Ошибка сохраниеня данных о запросе пользователя: {error}')

def give_chance(msg, what):
    with sqlite3.connect('info.db') as db:
        cursor = db.cursor()
        cursor.execute(f'SELECT {what} FROM info')
        alpha = cursor.fetchall()
        alpha = list(set(alpha))
        maby = None
        maby_similarity = 1
        for variant in alpha:
            name = variant[0]
            similarity = Levenshtein.distance(msg.lower(), name.lower()) / max(len(msg), len(name))
            if similarity < maby_similarity:
                maby_similarity = similarity
                maby = name
        if maby_similarity > 0.3 and len(msg) > 5:
            maby = None
        elif maby_similarity > 0.4 and len(msg) < 6:
            maby = None
        return maby