from rest_framework.serializers import ModelSerializer

from event.models import Event, AvailableTickets, Reservation


class TicketStatusSerializer(ModelSerializer):
    class Meta:
        model = AvailableTickets
        name = 'available_tickets'
        fields = ('ticket_type', 'price', 'amount', 'available')


class EventSerializer(ModelSerializer):
    tickets = TicketStatusSerializer(many=True,
                                     read_only=True)
    
    class Meta:
        model = Event
        name = 'event'
        fields = ('id', 'name', 'date', 'tickets')


class ReservationSerializer(ModelSerializer):

    class Meta:
        model = Reservation
        name = 'reservation'
        fields = ('client', 'created', 'ticket_type', 'amount')
