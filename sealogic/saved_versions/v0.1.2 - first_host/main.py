import requests
import time
from datetime import datetime
import pytz
import json
import os

from new_in import reg_amdin, new_in_sql, creat_excel, for_admins

offset = 0
token = 'delete'
URL = 'https://api.telegram.org/bot'

def send_document(chat_id, document_path, caption=None):
    url = f'https://api.telegram.org/bot{token}/sendDocument'
    params = {
        'chat_id': chat_id,
        'caption': caption
    }
    files = {
        'document': open(document_path, 'rb')
    }
    response = requests.post(url, params=params, files=files)
    if response.status_code == 200:
        print(f'Файл успешно отправлен пользователю: {user_id}')
    else:
        print(f'Ошибка при отправке файла пользователю: {user_id}')



def listen(URL, token, offset=0):
    while True:
        try:
            request = requests.get(f'{URL}{token}/getUpdates?offset={offset}').json()
            return request['result']
        except Exception:
            time.sleep(1)
            tz = pytz.timezone('Europe/Moscow')
            moscow = datetime.now(tz)
            print(f'Error getting updates, {moscow}')


def send_message(chat_id, text, buttons=None, document_path=None):
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    if document_path is not None:
        url = f'https://api.telegram.org/bot{token}/sendDocument'
        params = {
            'chat_id': chat_id,
            'document': open(document_path, 'rb')
        }
    else:
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

try:
    last_info = listen(URL, token)
except Exception:
    last_info = ''

while len(last_info) == 0:
    try:
        last_info = listen(URL, token)
        time.sleep(1)
    except Exception:
        time.sleep(1)
        continue

while True:
    try:
        last_update_info = last_info[len(last_info) - 1].get('update_id', None)
        old_last_time = datetime.strptime(for_admins(), '%Y-%m-%d %H:%M:%S')
        last_time = int(old_last_time.timestamp())
        tz = pytz.timezone('Europe/Moscow')
        moscow = datetime.now(tz)
        print(f'----start work at: {moscow} - by Moscow time----')
        break
    except Exception as error:
        print(f'Ошибка получения последних данных{error}')
        time.sleep(1)
        continue

while True:
    try:
        new_info = listen(URL, token, last_update_info)
        while len(new_info) == 0:
            new_info = listen(URL, token, last_update_info)
            time.sleep(1)
        now_update_info = new_info[len(new_info) - 1].get('update_id', None)
        if now_update_info > last_update_info:
            for elemen in new_info:
                try:
                    update_id = elemen.get('update_id', None)
                    if update_id > last_update_info:
                        if 'message' in elemen:
                            about_msg = elemen['message']
                            user_id = about_msg['from']['id']
                            chat_id = about_msg['chat']['id']
                            teg_user = about_msg['from']['username']
                            msg_id = about_msg['message_id']
                            first_name = about_msg['from']['first_name']
                            try:
                                last_name = about_msg['from']['last_name']
                            except Exception as error:
                                print(f'Ошибка получения фамилии: {error}')
                            try:
                                msg = about_msg['text']
                            except Exception as error:
                                msg = ''
                        elif 'callback_query' in elemen:
                            about_msg = elemen['callback_query']
                            user_id = about_msg['from']['id']
                            msg_id = about_msg['message']['message_id']
                            teg_user = about_msg['from']['username']
                            first_name = about_msg['from']['first_name']
                            last_name = about_msg['from']['last_name']
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
                        if reg_amdin(user_id) == 'Y' and chat_id == user_id:
                            try:
                                ####получаем таблицу на обновление
                                if not (about_msg['document']['file_id'] is None) and '.xlsx' in about_msg['document']['file_name']:
                                    send_message(user_id,
                                                 '⏳Обновляем сведения для пользователей.\n❗️Процесс может занять от нескольких секунд, до нескольких минут в зависимости от веса файла.')

                                    try:
                                        try:
                                            os.remove('bd.xlsx')
                                        except Exception:
                                            print('exel-базы файла не сущестовало, создаю новый')
                                        about_msg = elemen['message']
                                        file_id = about_msg['document']['file_id']
                                        download_url = f'https://api.telegram.org/bot{token}/getFile?file_id={file_id}'
                                        download_response = requests.get(download_url)
                                        file_info = download_response.json()
                                        file_path = file_info['result']['file_path']
                                        download_url = f'https://api.telegram.org/file/bot{token}/{file_path}'
                                        download_response = requests.get(download_url)
                                        with open('bd.xlsx', 'wb') as file:
                                            file.write(download_response.content)
                                        try:
                                            lol = new_in_sql()
                                        except Exception as error:
                                            print(f'Ошибка: {error}')
                                            lol = 'N'
                                    except Exception as error:
                                        print(f'Ошибка: {error}')
                                        lol = 'N'
                                    if lol == 'Y':
                                        print(f'✅Я успешно обновил таблицу, которую получил от пользователя: {user_id}')
                                        send_message(user_id,
                                                     '✅Я успешно обновил таблицу')
                                    else:
                                        print(f'❌Произошла ошибка сохранения новых данных, которые я получил от пользователя: {user_id}')
                                        send_document(user_id,
                                                      'error.gif',
                                                      '❌Произошла ошибка сохранения новых данных, пользователи имеют на руках устаревшие данные!\n❗️Проблема может быть вызвана новым оформлением файла exel, отправьте файл в старом формате или обратитесь к специалисту!')
                            except Exception:
                                if msg != '':
                                    msg = msg.lower()
                                    if msg == '/all' or msg == '/done' or msg == '/fail':
                                        try:
                                            send_message(user_id,
                                                     '⏳Формируем удобный для чтения файл, ожидайте.\n❗️Процесс может занять от нескольких секунд, до нескольких минут в зависимости от веса файла.')
                                            creat_excel(msg)
                                            send_document(user_id,
                                                          'output.xlsx', '🗂Вот ваш файл')
                                        except Exception as e:
                                            print(e)
                                            send_message(user_id,
                                                         '❌Произошла ошибка извлечения данных.\n❗️Проверьте наличие файла!')
                    time.sleep(0.3)
                except Exception as e:
                    print(f'Ошибка обработки сообщения пользователя {e}')
                    continue
            last_update_info = now_update_info
        else:
            time.sleep(0.5)
        try:
            remember = for_admins()
            new_time = datetime.strptime(remember, '%Y-%m-%d %H:%M:%S')
            new_time = int(new_time.timestamp())
            if new_time > last_time:
                last_time = new_time
                client, admins = for_admins(remember)
                if client is not None and admins is not None:
                    for userid in admins:
                        userid = userid[0]
                        try:
                            mail, client_id, pol, pod, pol_ru, pod_ru, soccoc, dem, many, lol, when = client
                            if pol == 'None':
                                pol = pol_ru
                            if pod == 'None':
                                pod = pod_ru
                            send_message(userid,
                                         f'Клиент выполнил успешный поиск:\nКонтакнтая почта: {mail}\nID клиента: {client_id}\nОткуда: {pol}\nКуда: {pod}\nО контейнерах: {soccoc} {dem} - {many} штук\nВремя поступления запроса: {when}')
                        except Exception as error:
                            print(f'Ошибка чтения и рассылки новго запроса из бд: {error}')
                elif client is not None and admins is None:
                    mail, client_id, pol, pod, pol_ru, pod_ru, soccoc, dem, many, lol, when = client
                    if pol == 'None':
                        pol = pol_ru
                    if pod == 'None':
                        pod = pod_ru
                    teguser =  requests.get(f'https://api.telegram.org/bot6675104047:AAFJIHEHFgoh28Dxow2TrRJa4LGWApNijm8/getChat?chat_id={client_id}').json()
                    teguser = teguser['result']['username']
                    if pod == 'None':
                        pod = ''
                    else:
                        pod = f'\nКуда: {pod}'
                    if not soccoc == 'None':
                        if dem == 'None':
                            dem = ''
                        containers = f'\nО контейнерах: {soccoc} {dem}'
                    else:
                        containers = ''
                    send_message(-1001727473350,
                                 f'Контакнтая почта: {mail}\nID клиента: {client_id}\nСсылка: @{teguser}\n\nИзвестные данные:\nОткуда: {pol}{pod}{containers}\nВремя поступления запроса: {when}\n#{teguser}')
        except Exception as error:
            print(f'Ошибка обновления новых запросов клиентов: {error}')
    except Exception as error:
        print(f'Непредвиденная Общая ошибка: {error}')
        try:
            last_update_info = now_update_info
            tz = pytz.timezone('Europe/Moscow')
            moscow = datetime.now(tz)
            print(f'----Restart working at: {moscow} - by Moscow time----')
        except Exception as error:
            tz = pytz.timezone('Europe/Moscow')
            moscow = datetime.now(tz)
            print(f'{moscow} -- Запуск цикла для получения последних данных после сбоя: {error}')
            while True:
                try:
                    last_update_info = last_info[len(last_info) - 1]['update_id']
                    tz = pytz.timezone('Europe/Moscow')
                    moscow = datetime.now(tz)
                    print(f'----Restart working at: {moscow} - by Moscow time----')
                    break
                except Exception:
                    continue
