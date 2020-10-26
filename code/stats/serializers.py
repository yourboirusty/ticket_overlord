from rest_framework import serializers


class TicketStatSerializer(serializers.Serializer):
    ticket_type = serializers.CharField(max_length=64)
    reservation_amount = serializers.IntegerField()
    reservation_avg_amount = serializers.IntegerField()
    sold_amount = serializers.IntegerField()
    profit = serializers.DecimalField(max_digits=19, decimal_places=2)


class EventStatSerializer(serializers.Serializer):
    event = serializers.CharField(max_length=64, source='__str__')
    reservation_amount = serializers.IntegerField()
    sold_amount = serializers.IntegerField()
    profit = serializers.DecimalField(max_digits=19, decimal_places=2)
