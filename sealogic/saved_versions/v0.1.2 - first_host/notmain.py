import requests
import time
from datetime import datetime
import pytz
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib as smtp
from langdetect import detect


####Мои скрипты
from sqlite_work import creat_tables, reg_user, reg_amdin, get_list, shablon, sql_get, sql_get_result, save_result, give_chance
####Скрипты для работы с бд, подробнее в файле sqlite_work.py
finder = []
ru_family = [
    'ru',
    'uk',
    'be',
    'bg',
    'si',
    'mk'
]
#массив обрабатываемых сейчас поисков

creat_tables()
####Создание бд для храниния данных о пользователях, подробнее о структуре бд в файле sqlite_work.py

offset = 0
token = 'delete'
URL = 'https://api.telegram.org/bot'



####Функция получения/отправки данных ТГ серверов
def listen(URL, token, offset=0):
    ####Мы расталкиваем сервер до тех пор, пока он нам нормально не ответит и только после нормального ответа мы передаем дальше данные, это помогает не ронять бота и 'продолжать работу' (точнее программы) даже при сбое
    while True:
        try:
            request = requests.get(f'{URL}{token}/getUpdates?offset={offset}').json()
            return request['result']
        except Exception:
            time.sleep(1)
            tz = pytz.timezone('Europe/Moscow')
            moscow = datetime.now(tz)
            print(f'Error getting updates, {moscow}')


def send_message(chat_id, text, buttons=None):
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    if buttons is None:
        params = {
            'chat_id': chat_id,
            'text': text
        }
    else:
        inline = {
            'inline_keyboard': buttons
        }
        params = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': json.dumps(inline)
        }
    requests.get(url, params=params)

def check_mail(mail, user_id):
    ####Работа с почтой (подкл к серверу, вход на свою почту, отправка ключа пользователю), при ошибке просим пользователя повторить поппытку позднее
    try:
        msg = MIMEMultipart()
        msg['From'] = 'your_mail@yandex.ru'
        msg['To'] = mail
        msg['Sibject'] = 'Код для регистрации'
        msg.attach(
            MIMEText('Спасибо за регистрацию!', 'plain')
        )
        server = smtp.SMTP_SSL('smtp.yandex.ru', 465)
        server.ehlo('your_mail@yandex.ru')
        server.login('your_mail@yandex.ru', 'token')
        server.auth_plain()
        server.send_message(msg)
        server.quit()
        ####Последний параметр я не передаю т.к. мне нужно подтверждение что это действительная почта пользователя и без этого я не да ему доступ
        result = reg_user(user_id=user_id, mail=mail)
        if result == 'error':
            return 'Внутренняя ошибка бота, просим повторить попытку через несколько минут'
        elif result == 'done':
            return 'Спасибо и добро пожаловать в telegram-бот sealogic⛴!'
    except Exception as er:
        print(er)
        return 'Проверьте правильностиь написания почты'


#####Запоминаем какой последний айди был у последнего сообщения до того момента как бот приступит к самой работе
try:
    last_info = listen(URL, token)
except Exception:
    last_info = ''

while len(last_info) == 0:
    try:
        last_info = listen(URL, token)
        time.sleep(5)
    except Exception:
        time.sleep(1)

while True:
    try:
        last_update_info = last_info[len(last_info) - 1]['update_id']
        tz = pytz.timezone('Europe/Moscow')
        moscow = datetime.now(tz)
        print(f'----start work at: {moscow} - by Moscow time----')
        break
    except Exception:
        continue

####Бесконечно слушаем клиентов, иначе быть не может :)
while True:
    try:
        tz = pytz.timezone('Europe/Moscow')
        moscow = datetime.now(tz)
        ####Получили свежие данные о сообщениях от сервера, нам важен айди сообщения
        new_info = listen(URL, token, last_update_info)
        while len(new_info) == 0:
            new_info = listen(URL, token, last_update_info)
            time.sleep(1)
        now_update_info = new_info[len(new_info) - 1].get('update_id', None)
        ####Проверям - нет личего новго в айди-холодильнике, открыаем его и закрываем в надежде на новенькое
        {'update_id': 658092186, 'callback_query': {'id': '8996108279250143521', 'from': {'id': 6389536977, 'is_bot': False, 'first_name': 'Tester', 'last_name': 'Hoster', 'username': 'GreatTester', 'language_code': 'en'}, 'message': {'message_id': 267, 'from': {'id': 6675104047, 'is_bot': True, 'first_name': 'ПОИСК sealogic', 'username': 'sealogic_search_bot'}, 'chat': {'id': 6389536977, 'first_name': 'Tester', 'last_name': 'Hoster', 'username': 'GreatTester', 'type': 'private'}, 'date': 1690363466, 'text': 'Быть может вы ищите: Амбарли?', 'reply_markup': {'inline_keyboard': [[{'text': 'Амбарли', 'callback_data': 'button1'}]]}}, 'chat_instance': '9016542805504358464', 'data': 'button1'}}


        if now_update_info > last_update_info:
            for elemen in new_info:
                update_id = elemen.get('update_id', None)
                ####Это что бы не слушать не новые сообщения, если убрать - будет реагировать на 1 прошлое сообщение пользователя
                if update_id > last_update_info:
                    try:
                        if 'message' in elemen:
                            about_msg = elemen['message']
                            user_id = about_msg['from']['id']
                            chat_id = about_msg['chat']['id']
                            teg_user = about_msg['from']['username']
                            msg_id = about_msg['message_id']
                            # try:
                            #    first_name = about_msg['from']['first_name']
                            #    last_name = about_msg['from']['last_name']
                            # except Exception as error:
                            #    print(f'Ошибка получения персональных данных о клиенте: {error}')
                            try:
                                msg = about_msg['text']
                            except Exception as error:
                                msg = ''
                        elif 'callback_query' in elemen:
                            about_msg = elemen['callback_query']
                            user_id = about_msg['from']['id']
                            msg_id = about_msg['message']['message_id']
                            teg_user = about_msg['from']['username']
                            #try:
                            #    first_name = about_msg['from']['first_name']
                            #    last_name = about_msg['from']['last_name']
                            #except Exception as error:
                            #    print(f'Ошибка получения персональных данных о клиенте: {error}')
                            about_msg = about_msg['message']
                            chat_id = about_msg['chat']['id']
                            try:
                                data = elemen['callback_query']['data']
                                variants = elemen['callback_query']['message']['reply_markup']['inline_keyboard']
                                stop = None
                                for elements in variants:
                                    for string in elements:
                                        callback = string['callback_data']
                                        if callback == data:
                                            msg = string['text']
                                            stop = 'Y'
                                            break
                                    if stop is not None:
                                        break
                            except Exception as error:
                                msg = ''
                        result = reg_user(user_id=user_id)
                        ####Если доступа нет - просим зарегистрироваться
                        if result == 'None' and not ('@' in msg and '.' in msg):
                            send_message(user_id,
                                         'Укажите, пожалуйста, ваш e-mail, чтобы мы могли убедиться, что Вы не робот:')
                        ####Если сообщение напоминает нам внешне почту - пробуем ей написать и авториззовать пользователя
                        elif result == 'None' and '@' in msg and '.' in msg:
                            lol = check_mail(mail=msg, user_id=user_id)
                            send_message(user_id, lol)
                            time.sleep(0.1)
                            lol = lol.lower()
                            if 'спасибо' in lol and user_id != 1462408293:
                                send_message(user_id,
                                             'Укажите откуда надо доставить груз?')
                            elif 'спасибо' in lol and user_id == 1462408293:
                                send_message(user_id,
                                             'Привет разработчик! :)')

                        elif result == 'Y' and user_id == chat_id:
                            ####реагируем на зарегистрированного создателя (для тестов, в последствии можно удалить, никакого особого функционала тут кроме добавления админов нет)
                            if user_id == 1462408293:
                                if msg != '':
                                    ####Добавление администрации
                                    if msg.lower()[0:len('добавить ')] == 'добавить ':
                                        msg = msg[len('добавить ') + 1:]
                                        ####админом омжет стать только зарегистрированный пользователь (ТГ вообще капризная и жадная на информацию штука в отличии от вк, обмениваем удобвство на гарантию работы блока)
                                        users = get_list()[1:len(get_list()) - 1].replace(',),', ' ').replace('(', '').replace(',)', '').split()
                                        for userid in users:
                                            try:
                                                user_info = requests.get(
                                                    f'https://api.telegram.org/bot{token}/getChat?chat_id={userid}').json()
                                                user_name = user_info['result']['username']
                                                time_user_id = user_info['result']['id']
                                                if user_name == msg:
                                                    users = []
                                                    ####Нашли админа - круто, нечего дальше массив пользователей держать, на свалку времен его, он и пустым нам поможет не получить соо что добавить не удалось
                                                    if reg_amdin(time_user_id, 'reg him/she') is None:
                                                        send_message(user_id,
                                                                     'Добавил в список админов.')
                                                        send_message(time_user_id,
                                                                     'Вас назначили администратором, мои поздравления!')
                                                    else:
                                                        send_message(user_id,
                                                                     'Этот пользователь уже является администратором!')
                                                    break
                                            except Exception:
                                                print('')
                                        ####Если не получилось найти и добавить пользователя - значит он не зарегистрировался в боте (почту к примеру верную и рабочую не выдал, а то и вовсе не писал боту)
                                        if len(users) != 0:
                                            send_message(user_id,
                                                         'Этот пользователь не доступен для выбора т.к. не прошел регистрацию')

                            elif msg != '':
                                ####Самое сложное - пользователь; finder - массив текущих поисковых запросов пользователей
                                if len(finder) == 0:
                                    finder.append(shablon(user_id))
                                else:
                                    a = 0
                                    for a in range(0, len(finder)):
                                        ####Если пользовательский id уже фигурирует в массиве запросов -> он делает запрос сейчас
                                        if finder[a].get('user_id', None) == user_id:
                                            a = -1
                                            break
                                    if a != -1:
                                        finder.append(shablon(user_id))
                                ####перебираем столбцы в таблице
                                for l in range(0, len(finder)):
                                    if finder[l]['user_id'] == user_id:
                                        elem = finder[l]
                                        ####Первая остановка и вопрос 'Укажите откуда необходимо доставить груз'
                                        if (msg.lower() == '/start' or msg.lower() == 'отменить') and not (finder[l]['POL'] is None and elem['POL_ru'] is None):
                                            if elem['Result'] is None:
                                                elem['Result'] = 'Fail'
                                                save_result(elem)

                                                send_message(user_id,
                                                             'Поиск отменен, ждем Ваш новый запрос!\nУкажите порт отгрузки.')
                                            else:
                                                send_message(user_id,
                                                             'Ожидаем Ваш новый запрос!\nУкажите порт отгрузки.')
                                            finder.remove(elem)
                                            break
                                        elif (msg.lower() == '/start' or msg.lower() == 'отменить') and elem['POL'] is None and elem['POL_ru'] is None:
                                            send_message(user_id,
                                                         'Ожидаем Ваш запрос!\nУкажите порт отгрузки.')
                                            break

                                        elif msg == '/contacts':
                                            send_message(user_id,
                                                         'Ждем Ваше письмо на почте info@sealogic.io\nС уважением, команда sealogic.io')

                                        else:
                                            if elem['POL_ru'] is None and elem['POL'] is None:
                                                language = detect(msg)
                                                if language in ru_family:
                                                    answer = sql_get(msg, 'pol_ru')
                                                    if answer == 'N':
                                                        msg = msg.title()
                                                        answer = sql_get(msg, 'pol_ru')
                                                else:
                                                    answer = sql_get(msg, 'pol')
                                                    if answer == 'N':
                                                        msg = msg.title()
                                                        answer = sql_get(msg, 'pol')


                                                if answer != 'N':
                                                    if language in ru_family:
                                                        elem['POL_ru'] = msg
                                                    else:
                                                        elem['POL'] = msg
                                                    send_message(user_id,
                                                                 'Порт отгрузки выбран.\nУкажите куда необходимо доставить груз')
                                                else:
                                                    if language in ru_family:
                                                        maby = (give_chance(msg, 'pol_ru'))
                                                    else:
                                                        maby = (give_chance(msg, 'pol'))
                                                    if maby is None:
                                                        send_message(user_id,
                                                                     f'Я не могу сам найти решение🤖. Вам поможет мой человек🧑🏻‍💻, напишите на почту info@sealogic.io, он вас уже ждет🫶🏼')
                                                    else:
                                                        buttons = [
                                                            [
                                                                {
                                                                    'text': maby,
                                                                    'callback_data': 'button1'
                                                                }
                                                            ]
                                                        ]
                                                        send_message(user_id,
                                                                     f'Возможно вы ищите: {maby}?', buttons)
                                                break
                                            ####Вторая остановка и вопрос 'Укажите куда необходимо доставить груз'
                                            elif elem['POD'] is None and elem['POD_ru'] is None:
                                                msg = msg.title()
                                                language = detect(msg)

                                                if language in ru_family:
                                                    answer = sql_get(msg, 'pod_ru')
                                                else:
                                                    answer = sql_get(msg, 'pod')

                                                if answer != 'N':
                                                    if language in ru_family:
                                                        elem['POD_ru'] = msg
                                                    else:
                                                        elem['POD'] = msg
                                                    answer = sql_get_result(elem)

                                                if answer != 'N':
                                                    buttons = [
                                                        [
                                                            {
                                                                'text': 'SOC',
                                                                'callback_data': 'button1'
                                                            },
                                                            {
                                                                'text': 'COC',
                                                                'callback_data': 'button2'
                                                            }
                                                        ]
                                                    ]
                                                    send_message(user_id,
                                                                 'Маршрут выбран.\nВыберите собственника контейнеров.',
                                                                 buttons)
                                                else:
                                                    if language in ru_family:
                                                        maby = (give_chance(msg, 'pod_ru'))
                                                    else:
                                                        maby = (give_chance(msg, 'pod'))

                                                    if maby is None:
                                                        elem['POD'] = None
                                                        elem['POD_ru'] = None
                                                        send_message(user_id,
                                                                     f'Я не могу сам найти решение🤖. Вам поможет мой человек🧑🏻‍💻, напишите на почту info@sealogic.io, он вас уже ждет🫶🏼')
                                                    else:
                                                        buttons = [
                                                            [
                                                                {
                                                                    'text': maby,
                                                                    'callback_data': 'button1'
                                                                }
                                                            ]
                                                        ]
                                                        send_message(user_id,
                                                                     f'Быть может вы ищите: {maby}?',
                                                                     buttons)
                                                break
                                            ###Третья остановка - тип контейнеров
                                            elif elem['SOC / COC'] is None:
                                                msg = msg.upper()
                                                answer = sql_get(msg, 'soccoc')
                                                if answer != 'N':
                                                    elem['SOC / COC'] = msg
                                                    answer = sql_get_result(elem)
                                                    if answer == 'N':
                                                        elem['SOC / COC'] = None

                                                if answer != 'N':
                                                    elem['SOC / COC'] = msg
                                                    buttons = [
                                                        [
                                                            {
                                                                'text': "20'",
                                                                'callback_data': "button1"
                                                            },
                                                            {
                                                                'text': "40'",
                                                                'callback_data': 'button2'
                                                            }
                                                        ]
                                                    ]
                                                    send_message(user_id,
                                                                 'Собственник выбран.\nВыберите размер контейнеров.',
                                                                 buttons)
                                                else:
                                                    send_message(user_id,
                                                                 'Введены не корректные данные. Пожалуйста, укажите размер контейнеров.')
                                                break
                                            ###Все еще про контейнеры - их размер
                                            elif elem['Dem'] is None:
                                                if msg == '20':
                                                    msg = "20'"
                                                elif msg == '40':
                                                    msg = "40'"
                                                answer = sql_get(msg, 'dem')

                                                if answer != 'N':
                                                    elem['Dem'] = msg
                                                    answer = sql_get_result(elem)

                                                if answer != 'N':
                                                    send_message(user_id,
                                                                 'Размер контейнеров выбран.\nУкажите число контейнеров.')
                                                else:
                                                    buttons = [
                                                        [
                                                            {
                                                                'text': "20'",
                                                                'callback_data': "button1"
                                                            },
                                                            {
                                                                'text': "40'",
                                                                'callback_data': 'button2'
                                                            }
                                                        ]
                                                    ]
                                                    send_message(user_id,
                                                                 'Укажите размер контейнеров.',
                                                                 buttons)
                                                break
                                            ###И вновь про контейнеры - количество
                                            elif elem['many'] is None:
                                                if msg.isdigit():
                                                    elem['many'] = msg
                                                    send_message(user_id,
                                                                 'Количество контейнеров выбрано.')
                                                    answer = sql_get_result(elem)
                                                    answer = list(set(answer))
                                                    lol = []
                                                    for ele in answer:
                                                        currency = ele[1]
                                                        if currency == 'USD':
                                                            many = ele[0]
                                                            if '.' in many:
                                                                many = many[:many.find('.')]
                                                                many = many.replace('.', '')
                                                            many = int(many)
                                                            lol.append(many)
                                                    mini = 9999
                                                    maxi = 0
                                                    for ele in lol:
                                                        if ele > maxi:
                                                            maxi = ele

                                                        if ele < mini:
                                                            mini = ele
                                                    elem['Result'] = 'Done'
                                                    save_result(elem)
                                                    send_message(user_id,
                                                                 f'Количество результатов:{len(answer)} \n Стоимость вашего заказа: \nМаскимум: {maxi * int(msg)}USD\nМинимум: {mini * int(msg)}USD\nДля предоставления вам большей информации с вами свяжется наш менеджер')
                                                else:
                                                    send_message(user_id,
                                                                 'Укажите натуральное число контейнеров.')
                                                break
                                            ###Конечная остановка!
                                            else:
                                                buttons = [
                                                    [
                                                        {
                                                            'text': "отменить",
                                                            'callback_data': "button1"
                                                        }
                                                    ]
                                                ]
                                                send_message(user_id,
                                                             'Мы выполнили поиск по всем вашим критериям, если Вам нужено создать новый запрос - нажмите /start в меню или нажмите кнопку отменить ниже',
                                                             buttons)
                        time.sleep(0.3)
                    except Exception as eror:
                        try:
                            send_message(user_id, 'Я не могу сам найти решение🤖. Вам поможет мой человек🧑🏻‍💻, напишите на почту info@sealogic.io, он вас уже ждет🫶🏼')
                        except Exception as error:
                            print(f'Не удалось уведомить клиента об ошибке: {error}')
                        print(f'Ошибка обработки сообщения пользовтеля: {eror}')
                        continue

            last_update_info = now_update_info
        else:
            time.sleep(0.35)
    except Exception as error:
        print(f'Непредвиденная Общая ошибка: {error}')
        try:
            last_update_info = now_update_info
        except Exception as error:
            print(f'Повторное получение последних данных после сбоя: {error}')
            while True:
                try:
                    last_update_info = last_info[len(last_info) - 1]['update_id']
                    tz = pytz.timezone('Europe/Moscow')
                    moscow = datetime.now(tz)
                    print(f'----Restart working at: {moscow} - by Moscow time----')
                    break
                except Exception:
                    continue