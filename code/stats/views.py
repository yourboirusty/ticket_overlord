from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import F, Sum, Case, When, Avg
from event.models import Event, AvailableTickets
from stats.serializers import EventStatSerializer, TicketStatSerializer


class TicketStatsViewset(ViewSet):
    def get_queryset(self):
        annotations = dict()
        annotations['reservation_amount'] = Sum('reservations__amount')
        annotations['reservation_avg_amount'] = Avg('reservations__amount')
        annotations['sold_amount'] = Sum(
         Case(
            When(reservations__validated=True,
                 then=F('reservations__amount')),
            default=0)
        )
        annotations['profit'] = Sum(
         Case(
            When(reservations__validated=True,
                 then=F('reservations__amount') * F('price')),
            default=0)
        )
        return AvailableTickets.objects.all().values('ticket_type').annotate(
            **annotations
        )

    def list(self, request):
        queryset = self.get_queryset()
        serializer = TicketStatSerializer(queryset, many=True)
        return Response(serializer.data)


class EventStatsViewset(ViewSet):
    def list(self, request):
        queryset = Event.objects.all()
        serializer = EventStatSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_profit(self, request):
        queryset = Event.objects.all().annotate(
            profit=Sum(
                F('tickets__reservations__amount') * F('tickets__price')
            )
        ).order_by('-profit')[:5]
        serializer = EventStatSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_popular(self, request):
        queryset = Event.objects.all().annotate(
            reservation_amount=Sum(
                F('tickets__reservations__amount')
            )
        ).order_by('-reservation_amount')[:5]
        serializer = EventStatSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_selling(self, request):
        case = Case(
            When(tickets__reservations__validated=True,
                 then=F('tickets__reservations__amount')),
            default=0)
        queryset = Event.objects.all().annotate(
            sold_amount=Sum(case)
            ).order_by('-sold_amount')[:5]
        serializer = EventStatSerializer(queryset, many=True)
        return Response(serializer.data)
