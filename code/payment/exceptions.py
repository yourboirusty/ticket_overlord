from django.core.exceptions import ValidationError


class InvalidReservation(ValidationError):
    pass


class MissingReservation(ValidationError):
    pass


class AlreadyPaidError(ValidationError):
    pass


class CardError(Exception):
    pass


class PaymentError(Exception):
    pass


class CurrencyError(Exception):
    pass
