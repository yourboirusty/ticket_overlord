from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from event.models import Event, AvailableTickets, Reservation
from rest_framework.permissions import IsAuthenticated
from event.serializers import (EventSerializer,
                               TicketStatusSerializer,
                               ReservationSerializer)


class TicketStatusViewset(mixins.RetrieveModelMixin,
                          GenericViewSet):
    queryset = AvailableTickets.objects.all()
    serializer_class = TicketStatusSerializer


class EventViewset(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class ReservationViewset(mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.DestroyModelMixin,
                         GenericViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Reservation.objects.all()

    def get_queryset(self):
        user = self.request.user
        return Reservation.objects.filter(client_id=user.id)
