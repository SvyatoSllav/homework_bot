"""Телеграмм бот проверяющий статус проверки домашней работы."""

import logging
import os
import time
from http import HTTPStatus
from sys import stdout
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv

from exception import (
    APIResponseIsNotDict,
    APIResponseIsIncorrect,
    EndPointIsNotAccesed,
    HTTPStatusCodeIncorrect,
    HomeworkValueIncorrect,
    VariableNotExists,
    InvalidJSONTransform,
    NoStatusInResponse,
)

import requests

import telegram

API_RESPONSE_TYPE = Dict[str, Union[int, list]]
HOMEWORK_LIST_TYPE = List[Optional[Dict[str, Union[str, int]]]]

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s'
)
handler = logging.StreamHandler(
    stream=stdout
)
handler.setFormatter(formatter)
logger.addHandler(handler)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение с статусом обработки дз."""
    try:
        logger.info('Начата отправка сообщения в телеграмм')
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
        logger.info(f'Сообщение {message} было отправлено')
    except Exception as error:
        logger.error(f'Ошибка при отправке {message} сообщения: {error}')


def get_api_answer(current_timestamp: int) -> API_RESPONSE_TYPE:
    """Возвращает словарь за прошедшие дни."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.RequestException as error:
        message = f'Сбой при запросе к эндпоинту: {error}'
        logger.error(message)
        raise EndPointIsNotAccesed(message)
    status_code = homework.status_code
    if status_code != HTTPStatus.OK:
        message = f'Yandex API недоступен, код ошибки: {status_code}'
        logger.error(message)
        raise HTTPStatusCodeIncorrect(message)
    try:
        homework_json = homework.json()
    except Exception as error:
        message = f'Сбой при переводе в формат json: {error}'
        logger.error(message)
        raise InvalidJSONTransform(message)
    return homework_json


def check_response(response: API_RESPONSE_TYPE) -> HOMEWORK_LIST_TYPE:
    """Проверяет валидность ответа и возвращает список данных работ."""
    if type(response) == list:
        response = response[0]
    if type(response) != dict:
        response_type = type(response)
        message = f'Ответ пришел в неккоректном формате: {response_type}'
        logger.error(message)
        raise APIResponseIsNotDict(message)
    if 'current_date' and 'homeworks' not in response:
        message = 'В ответе отсутствуют необходимые ключи'
        logger.error(message)
        raise APIResponseIsIncorrect(message)
    homework = response.get('homeworks')
    if type(homework) != list:
        message = 'Неккоректное значение в ответе у домашней работы'
        logger.error(message)
        raise HomeworkValueIncorrect(message)
    return homework


def parse_status(homework: HOMEWORK_LIST_TYPE) -> str:
    """Проверяет статус проверки дз."""
    if homework.get('homework_name') is None:
        message = 'Отсутствует имя домашней работы'
        logger.error(message)
        raise KeyError(message)
    homework_name = homework.get('homework_name', 'Homework_no_name')
    if homework.get('status') not in HOMEWORK_STATUSES:
        message = ('недокументированный статус домашней работы ,'
                   'обнаруженный в ответе API')
        logger.error(message)
        raise NoStatusInResponse(message)
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет наличие переменных в локальном хранилище."""
    is_exists = all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])
    return is_exists


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Отсутствует критически важная для работы переменная'
        logger.critical(message)
        raise VariableNotExists(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    send_message(bot, 'Бот стартовал')
    current_timestamp = int(time.time())
    LAST_ERROR = ''
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logger.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            if message != LAST_ERROR:
                LAST_ERROR = message
                send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)

if __name__ == '__main__':
    main()
