from rest_framework.serializers import ModelSerializer, ValidationError

from event.models import Event, AvailableTickets, Reservation


class TicketStatusSerializer(ModelSerializer):
    class Meta:
        model = AvailableTickets
        name = 'available_tickets'
        fields = ('id', 'ticket_type', 'price', 'amount', 'available')


class EventSerializer(ModelSerializer):
    class Meta:
        model = Event
        name = 'event'
        fields = ('id', 'name', 'date', 'tickets')


class DetailedEventSerializer(ModelSerializer):
    tickets = TicketStatusSerializer(many=True)
    class Meta:
        model = Event
        name = 'event'
        fields = ('id', 'name', 'date', 'tickets')

class ReservationSerializer(ModelSerializer):

    class Meta:
        model = Reservation
        name = 'reservation'
        fields = ('id', 'created', 'ticket_type', 'amount')

    def validate(self, data):
        user = self.context['request'].user
        ticket = data['ticket_type']
        q = Reservation.objects.filter(client=user, ticket_type=ticket)
        if q.count() != 0:
            raise ValidationError("Reservation has already been made")

    def create(self, validated_data):
        validated_data['client'] = self.context['request'].user
        obj = Reservation.objects.create(**validated_data)
        return obj