"""Телеграмм бот проверяющий статус проверки домашней работы."""

import logging
import os
import time
from http import HTTPStatus
from sys import stdout
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv

from exception import (
    APIReponseIsNotDict,
    APIResponseIsIncorrect,
    HTTPStatusCodeIncorrect,
    HomeworkValueIncorrect,
    InvalidChatId,
    InvalidPracticumToken,
    InvalidTelegramToken,
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
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message)
        logging.info(f'Сообщение {message} было отправлено')
    except Exception as error:
        logging.error(f'Ошибка при отправке {message} сообщения: {error}')


def get_api_answer(current_timestamp: int) -> API_RESPONSE_TYPE:
    """Возвращает словарь за прошедшие дни."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    homework = requests.get(
        url=ENDPOINT,
        headers=HEADERS,
        params=params
    )
    status_code = homework.status_code
    if status_code != HTTPStatus.OK:
        message = f'Yandex API недоступен, код ошибки: {status_code}'
        logging.error(message)
        raise HTTPStatusCodeIncorrect
    homework_json = homework.json()
    return homework_json


def check_response(response: API_RESPONSE_TYPE) -> HOMEWORK_LIST_TYPE:
    """Проверяет валидность ответа и возвращает список данных работ."""
    if type(response) == list:
        response = response[0]
    if type(response) != dict:
        response_type = type(response)
        logging.error(f'Ответ пришел в неккоректном формате: {response_type}')
        raise APIReponseIsNotDict
    if 'current_date' and 'homeworks' not in response:
        logging.error('В ответе отсутствуют необходимые ключи')
        raise APIResponseIsIncorrect
    homework = response.get('homeworks')
    if type(homework) != list:
        logging.error('Неккоректное значение в ответе у домашней работы')
        raise HomeworkValueIncorrect
    return homework


def parse_status(homework: HOMEWORK_LIST_TYPE) -> str:
    """Проверяет статус проверки дз."""
    if homework.get('homework_name') is None:
        logging.error('Отсутствует имя домашней работы')
        raise KeyError('Отсутствует имя домашней работы')
    homework_name = homework.get('homework_name', 'Homework_no_name')
    if homework.get('status') not in HOMEWORK_STATUSES:
        logging.error('недокументированный статус домашней работы ,'
                      'обнаруженный в ответе API')  
        raise NoStatusInResponse
    homework_status = homework.get('status')
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверяет наличие переменных в локальном хранилище."""
    is_exists = (PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID)
    return is_exists


def token_existing_exception_raising() -> Exception:
    """Возвращает соответствующие исключения у пустых переменных."""
    if not PRACTICUM_TOKEN:
        logging.critical('Отсутствует PRACTICUM_TOKEN')
        return InvalidPracticumToken
    if not TELEGRAM_TOKEN:
        logging.critical('Отсутствует TELEGRAM_TOKEN')
        return InvalidTelegramToken
    if not TELEGRAM_CHAT_ID:
        logging.critical('Отсутствует TELEGRAM_CHAT_ID')
        return InvalidChatId


def main() -> None:
    """Основная логика работы бота."""
    LAST_ERROR = ''
    if not check_tokens():
        raise token_existing_exception_raising()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logging.debug('Отсутствие в ответе новых статусов')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            if message != LAST_ERROR:
                LAST_ERROR = message
                send_message(bot, message)
            time.sleep(RETRY_TIME)
        else:
            pass


if __name__ == '__main__':
    main()
