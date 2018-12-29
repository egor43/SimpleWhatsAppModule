# -*- coding: utf-8 -*-

""" Модуль предоставляет удобный доступ к API WhatsApp
    Ответственный: Мышко Е.В.
"""
import whatsapp_utils
import json


# Хост на котором расположен клиент с API
API_HOST = 'https://192.168.99.101:9090'
# Версия API
API_VER = 'v1'


# Методы входа и авторизации (получение маркера доступа)

def first_login(username, password, new_password):
    """
    Метод API First Login
    https://developers.facebook.com/docs/whatsapp/api/users/login
    :param username: имя пользователя
    :param password: пароль пользователя
    :param new_password: новый пароль пользователя
    :return: словарь с токеном доступа и временем его жизни. Формат: {'token': value, 'token_expires': value}
    """
    if not username:
        raise Exception('Отсутствует параметр username')
    if not password:
        raise Exception('Отсутствует параметр password')
    if not new_password:
        raise Exception('Отсутствует параметр new_password')

    if not whatsapp_utils.check_password(new_password):
        raise Exception('Недопустимый новый пароль')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.basic_authorization_headers(username, password)}

    # Заполняем тело запроса
    body_raw = {'new_password': new_password}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'users/login')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    users = api_response[0].get('users', [{}])
    token = users[0].get('token')
    expires = users[0].get('expires_after')

    if not token:
        raise Exception('Не удалось получить токен доступа')

    result = {'token': token, 'token_expires': expires}

    return result

def standart_login(username, password):
    """
        Метод API Standard Login
        https://developers.facebook.com/docs/whatsapp/api/users/login
        :param username: имя пользователя
        :param password: пароль пользователя
        :return: словарь с токеном доступа и временем его жизни. Формат: {'token': value, 'token_expires': value}
        """
    if not username:
        raise Exception('Отсутствует параметр username')
    if not password:
        raise Exception('Отсутствует параметр password')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.basic_authorization_headers(username, password)}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'users/login')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, "{}", headers, True)

    # Разбираем ответ
    users = api_response[0].get('users', [{}])
    token = users[0].get('token')
    expires = users[0].get('expires_after')

    if not token:
        raise Exception('Не удалось получить токен доступа')

    result = {'token': token, 'token_expires': expires}

    return result


# Методы регистрации

def registration_code(token, country_code, phone, cert, pin=None):
    """
    Метод API Registration code (запрашивает код регистрации)
    https://developers.facebook.com/docs/whatsapp/api/account
    :param token: токен доступа
    :param country_code: код страны
    :param phone: номер телефона без кода страны
    :param cert: сертификат vname в кодировке Base64
    :param pin: шестизначный pin (при двухфакторной проверке)
    :return: результат запроса на регистрацию.
             Возможные значения: created - успешно зарегистрирован
                                 accepted - необходимо завершить регистрацию
                                 error - возникла ошибка
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not country_code:
        raise Exception('Отсутствует параметр country_code')
    if not phone:
        raise Exception('Отсутствует параметр phone')
    if not cert:
        raise Exception('Отсутствует параметр cert')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Заполняем тело запроса
    body_raw = {'сс': country_code,
                'phone_number': phone,
                'method': 'sms',
                'cert': cert}

    if pin:
        body_raw['pin'] = pin

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'account')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    if api_response[1] == 201:
        return 'created'

    if api_response[1] == 202:
        return 'accepted'

    return 'error'

def finish_registration(token, code):
    """
    Метод API Registration code (завершение регистрации)
    https://developers.facebook.com/docs/whatsapp/api/account
    Внимание: Если вы регистрируете аккаунт повторно, по завершении регистрации необходимо перезапустить Coreapp.
    :param token: токен доступа
    :param code: код полученный от WhatsApp
    :return: результат запроса на завершение регистрации.
             Возможные значения: created - успешно зарегистрирован
                                 error - возникла ошибка
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not country_code:
        raise Exception('Отсутствует параметр code')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Заполняем тело запроса
    body_raw = {'code': code}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'account/verify')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    if api_response[1] == 201:
        return 'created'

    return 'error'


# Методы проверки контактов

def check_contacts(token, contacts, blocking='wait'):
    """
    Метод API Contacts
    https://developers.facebook.com/docs/whatsapp/api/contacts
    :param token: токен доступа
    :param contacts: список номеров для проверки
    :param blocking(='wait'): режим проверки. https://developers.facebook.com/docs/whatsapp/api/contacts#blocking
    :return: список контактов
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not contacts:
        raise Exception('Отсутствует параметр contacts')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Заполняем тело запроса
    body_raw = {'blocking': blocking,
                'contacts': contacts}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'contacts')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    result = api_response[0].get('contacts', [])

    return result


# Методы загрузки медиа в WhatsApp

def upload_file(token, mime_type, attachment):
    """
    Метод API Media
    https://developers.facebook.com/docs/whatsapp/api/media#upload
    :param token: токен доступа
    :param mime_type: MIME тип вложения
    :param attachment: вложение в бинарном виде
    :return: идентификатор загруженного файла
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not mime_type:
        raise Exception('Отсутствует параметр mime_type')
    if not attachment:
        raise Exception('Отсутствует параметр attachment')

    if len(attachment) > 64000000:
        raise Exception('Превышен размер вложения (64000000 байт)')

    if not whatsapp_utils.check_mime_type(mime_type):
        raise Exception('Недопустимый тип вложения')

    # Заполняем заголовки
    headers = {'Content-Type': mime_type,
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'media')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, attachment, headers, True)

    # Разбираем ответ
    media = api_response[0].get('media', [{}])
    media_id = media[0].get('id')

    if not media_id:
        raise Exception('Не удалось загрузить вложение')

    return media_id


# Методы отправки сообщений

def send_text_message(token, recipient, text):
    """
    Метод API Messages
    https://developers.facebook.com/docs/whatsapp/api/messages
    :param token: токен доступа
    :param recipient: whatsapp-id получателя
    :param text: текст сообщения
    :return: идентификатор отправленного сообщения
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not recipient:
        raise Exception('Отсутствует параметр recipient')
    if not text:
        raise Exception('Отсутствует параметр text')

    if len(text) > 4096:
        raise Exception('Превышен размер сообщения (4096 символов)')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Заполняем тело запроса
    body_raw = {'recipient_type': 'individual',
                'to': recipient,
                'type': 'text',
                'text': {'body': text}}

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'messages')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    messages = api_response[0].get('messages', [{}])
    message_id = messages[0].get('id')

    if not message_id:
        raise Exception('Не удалось отправить сообщение')

    return message_id

def send_media_message(token, recipient, type, media_id):
    """
    Метод API Messages
    https://developers.facebook.com/docs/whatsapp/api/messages
    :param token: токен доступа
    :param recipient: whatsapp-id получателя
    :param type: тип сообщения. Возможные значения: 'audio', 'document', 'image'
    :return: идентификатор отправленного сообщения
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    if not recipient:
        raise Exception('Отсутствует параметр recipient')
    if not type:
        raise Exception('Отсутствует параметр type')
    if not media_id:
        raise Exception('Отсутствует параметр media_id')

    # Заполняем заголовки
    headers = {'Content-Type': 'application/json',
               'Authorization': whatsapp_utils.bearer_authorization_headers(token)}

    # Заполняем тело запроса
    body_raw = {'recipient_type': 'individual',
                'to': recipient,
                'type': type}

    if type == 'audio':
        body_raw['audio'] = {'id': media_id}
    elif type == 'image':
        body_raw['image'] = {'id': media_id}
    elif type == 'document':
        body_raw['document'] = {'id': media_id}
    else:
        raise Exception('Отсутствует параметр media_id')

    # Получаем адрес запроса
    address = whatsapp_utils.get_request_address(API_HOST, API_VER, 'messages')

    # Выполняем запрос
    api_response = whatsapp_utils.post_request(address, json.dumps(body_raw), headers, True)

    # Разбираем ответ
    messages = api_response[0].get('messages', [{}])
    message_id = messages[0].get('id')

    if not message_id:
        raise Exception('Не удалось отправить сообщение')

    return message_id

