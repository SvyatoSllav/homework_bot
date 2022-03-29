"""Исключения при проверке валидности переменных."""


class InvalidPracticumToken(Exception):
    """Возникает из-за некорректности токена Яндекс Практикума."""

    message = 'Был передан некорректный токен Яндекс Практикуме'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class InvalidTelegramToken(Exception):
    """Возникает из-за некорректности телеграмм токена."""

    message = 'Был передан некорректный телеграмм токен.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class InvalidChatId(Exception):
    """Возникает из-за некорректности id чата."""

    message = 'Был передан некорректный чат id.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class HTTPStatusCodeIncorrect(Exception):
    """Возникает при коде состояния HTTP отличном от 200."""

    message = 'При подключении к серверу что-то пошло не так.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class APIReponseIsNotDict(Exception):
    """Возникает когда ответ не является списком."""

    message = 'Ответ не является словарём.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class APIResponseIsIncorrect(Exception):
    """Возникает при некорректном содержимом ответа."""

    message = 'Содержимое ответа некорректно.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class HomeworkValueIncorrect(Exception):
    """Возникает при неправильном значении домашней работы."""

    message = 'Содержимое домашней работы некорректно.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)


class NoStatusInResponse(Exception):
    """Возникает при некорректном значении статуса проверки задания."""

    message = 'Статус проверки домашней работы не опознан.'

    def __init__(self):
        """Печатает сообщение об ошибке в консоль."""
        super().__init__(self.message)
