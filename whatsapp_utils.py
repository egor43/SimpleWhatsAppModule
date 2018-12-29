# -*- coding: utf-8 -*-

""" Модуль предоставляет набор дополнительных функций
    Ответственный: Мышко Е.В.
"""

import base64
import json
import requests
import re

# Коды успешного запроса
SUCCESS_CODE = [200, 201, 202]
# Поддерживаемые MIME типы
SUPPORTED_MIME_TYPES = ['application/pdf',
                        'application/vnd.ms-powerpoint',
                        'application/msword',
                        'image/png',
                        'image/jpeg',
                        'audio/aac',
                        'audio/mpeg',
                        'audio/ogg']

def post_request(address, data, headers=None, convert_json=False):
    """
    Возвращает результат POST запроса на указанный адрес
    :param address: адрес запроса
    :param data: тело запроса
    :param headers: заголовки запроса
    :param convert_json: флаг, определяющий необходимость конвертации ответа в json
    :return: результат запроса, код статуса
    """
    if not address:
        raise Exception('Отсутствует параметр address')

    response = requests.post(address, data=data, headers=headers, verify=False)

    if response.status_code not in SUCCESS_CODE:
        error_msg = 'Не удалось выполнить запрос.\n'
        error_msg += construct_error_details(address=str(address),
                                             headers=str(headers),
                                             data=str(data),
                                             response=str(response.text),
                                             headers_resp=str(response.headers),
                                             status_code=str(response.status_code))
        raise Exception(error_msg)
    if convert_json:
        return response.json(), response.status_code
    return response.text, response.status_code

def get_request(address, headers=None, convert_json=False):
    """
    Возвращает результат GET запроса на указанный адрес
    :param address: адрес запроса
    :param headers(=None): заголовки запроса
    :param is_json(=False): флаг, определяющий необходимость конвертации ответа в json
    :return: результат запроса, код статуса
    """
    if not address:
        raise Exception('Отсутствует параметр address')

    response = requests.get(address, headers=headers, verify=False)

    if response.status_code not in SUCCESS_CODE:
        error_msg = 'Не удалось выполнить запрос.\n'
        error_msg += construct_error_details(address=str(address),
                                             headers=str(headers),
                                             response=str(response.text),
                                             headers_resp=str(response.headers),
                                             status_code=str(response.status_code))
        raise Exception(error_msg)
    if convert_json:
        return response.json(), response.status_code
    return response.text, response.status_code

def construct_error_details(**kwargs):
    """
    Возвращает строку с подготовленную для детализации ошибки
    :param kwargs: параметры для детализации
    :return: строка с детальным описанием
    """
    result = ''
    for key in kwargs:
        result += '{key}: {value}\n'.format(key=key, value=str(kwargs[key]))
    return result

def get_request_address(api_host, api_version, api_method):
    """
    Возвращает адрес для запроса
    :param api_host: хост на котором расположен api клиент
    :param api_version: версия api
    :param api_method: метод api к которому необходимо создать запрос
    :return: адрес запроса
    """
    if not api_host:
        raise Exception('Отсутствует параметр api_host')
    if not api_version:
        raise Exception('Отсутствует параметр api_version')
    if not api_method:
        raise Exception('Отсутствует параметр api_method')

    return '{host}/{version}/{method}'.format(host=api_host, version=api_version, method=api_method)

def check_password(password):
    """
    Проверяет пароль на соответствие требованиям WhatsApp
    :param password: пароль
    :return: результат проверки
    """
    if not password:
        raise Exception('Отсутствует параметр password')
    # Преобразуем в строку
    password = str(password)

    # Проверка длины:
    if (len(password) < 8) or (len(password) > 64):
        return False

    # Проверка на наличие цифрового символа
    if not re.search(r'\d', password):
        return False

    # Проверка на наличие символа в Uppercase
    if not re.search(r'[A-Z]', password):
        return False

    # Проверка на наличие символа в Lowercase
    if not re.search(r'[a-z]', password):
        return False

    # Проверка на наличие спецсимволов
    if not re.search(r'[\!\"\#\$\%\&\\\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\]\^\_\`\{\|\}\~]', password):
        return False

    return True

def basic_authorization_headers(username, password):
    """
    Возвращает значение заголовка для авторизации типа Basic
    :param username: имя пользователя
    :param password: пароль
    :return: Значание заголовка Authorization
    """
    if not username:
        raise Exception('Отсутствует параметр username')
    if not password:
        raise Exception('Отсутствует параметр password')
    header = 'Basic {auth_info}'
    auth_info = str(username) + ':' + str(password)
    auth_info = base64.b64encode(auth_info.encode()).decode()
    header = header.format(auth_info=auth_info)
    return header

def bearer_authorization_headers(token):
    """
    Возвращает значение заголовка для авторизации типа Bearer
    :param token: токен авторизации
    :return: Значание заголовка Authorization
    """
    if not token:
        raise Exception('Отсутствует параметр token')
    header = 'Bearer {token}'
    header = header.format(token=token)
    return header

def check_mime_type(mime_type):
    """
    Проверяет тип на допустимый для загрузки в WhatsApp
    :param mime_type: MIME тип файла
    :return: результат проверки
    """
    if not mime_type:
        raise Exception('Отсутствует параметр mime_type')
    if mime_type in SUPPORTED_MIME_TYPES:
        return True
    return False