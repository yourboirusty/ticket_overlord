from dynamic_rest.serializers import DynamicModelSerializer
from dynamic_rest.fields import DynamicRelationField
from event.models import Event, AvailableTickets


class TicketStatusSerializer(DynamicModelSerializer):
    class Meta:
        model = AvailableTickets
        name = 'available_tickets'
        fields = ('ticket_type', 'available')


class EventSerializer(DynamicModelSerializer):
    tickets = DynamicRelationField('TicketStatusSerializer',
                                   deferred=False,
                                   many=True)

    class Meta:
        model = Event
        name = 'event'
        fields = ('id', 'name', 'date')
