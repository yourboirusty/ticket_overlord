from rest_framework.serializers import ModelSerializer, ValidationError
from rest_framework import serializers
from payment.models import Payment
from event.models import Reservation


class PaymentProcessSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=64)
    currency = serializers.CharField(max_length=3)


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        name = 'payment'
        fields = ('id',
                  'full_price',
                  'error',
                  'payment_status')
        read_only_fields = ('__all__', )


class PaymentCreationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    reservation_id = serializers.IntegerField()

    def validate(self, data):
        user = self.context['request'].user
        reservation = Reservation.objects.filter(id=data['reservation_id'],
                                                 client=user).count()
        if not reservation:
            raise ValidationError("No such reservation")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        reservation = Reservation.objects.get(
            id=validated_data['reservation_id'])
        obj = Payment.objects.create(client=user, reservation=reservation)
        return obj
