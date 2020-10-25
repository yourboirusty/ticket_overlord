from django.core.exceptions import ValidationError


class EventStartedError(ValidationError):
    pass


class NotEnoughTicketsError(ValidationError):
    pass