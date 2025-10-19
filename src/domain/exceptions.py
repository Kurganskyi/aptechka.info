"""
Domain exceptions - исключения бизнес-логики
"""


class DomainException(Exception):
    """Базовое исключение домена"""
    pass


class UserNotFoundException(DomainException):
    """Пользователь не найден"""
    pass


class ProductNotFoundException(DomainException):
    """Продукт не найден"""
    pass


class OrderNotFoundException(DomainException):
    """Заказ не найден"""
    pass


class PaymentException(DomainException):
    """Ошибка платежа"""
    pass


class PaymentAlreadyExistsException(PaymentException):
    """Платеж уже существует"""
    pass


class PaymentExpiredException(PaymentException):
    """Платеж истек"""
    pass


class InsufficientFundsException(PaymentException):
    """Недостаточно средств"""
    pass


class TestAlreadyCompletedException(DomainException):
    """Тест уже пройден"""
    pass


class TestNotFoundException(DomainException):
    """Тест не найден"""
    pass


class AdminPermissionException(DomainException):
    """Недостаточно прав администратора"""
    pass
