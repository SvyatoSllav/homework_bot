"""Исключения при проверке валидности переменных."""


class VariableNotExists(Exception):
    """Возникает при отсутствии обязательной переменной."""


class HTTPStatusCodeIncorrect(Exception):
    """Возникает при коде состояния HTTP отличном от 200."""


class APIResponseIsNotDict(Exception):
    """Возникает когда ответ не является списком."""


class APIResponseIsIncorrect(Exception):
    """Возникает при некорректном содержимом ответа."""


class HomeworkValueIncorrect(Exception):
    """Возникает при неправильном значении домашней работы."""


class NoStatusInResponse(Exception):
    """Возникает при некорректном значении статуса проверки задания."""


class InvalidJSONTransform(Exception):
    """Возникает при ошибке преобразования ответа в json формат."""


class EndPointIsNotAccesed(Exception):
    """Возникает при неизвестной ошибке при запросе к ендпоинту."""
