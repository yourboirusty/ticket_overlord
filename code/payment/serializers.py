from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework import serializers
from payment.models import Payment
from event.models import Reservation


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        name = 'payment'
        fields = ('id',
                  'full_price',
                  'amount',
                  'currency',
                  'error',
                  'payment_status')
        read_only_fields = ('__all__', )


class PaymentCreationSerializer(serializers.Serializer):
    reservation_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        reservation = Reservation.objects.filter(id=data['reservation_id'],
                                                 client=user).count()
        if not reservation:
            raise ValidationError("No such reservation")

    def create(self, validated_data):
        user = self.context['request'].user
        reservation = Reservation.objects.get(
            id=validated_data['reservation_id'])
        obj = Payment.objects.create(client=user, reservation=reservation)
        return obj
