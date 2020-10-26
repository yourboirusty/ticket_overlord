from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from payment.exceptions import MissingReservation, InvalidReservation
from payment.serializers import (PaymentSerializer,
                                 PaymentCreationSerializer,
                                 PaymentProcessSerializer)
from payment.models import Payment


class PaymentViewset(mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.CreateModelMixin,
                     GenericViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreationSerializer
        if self.action =='pay':
            return PaymentProcessSerializer
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(client=user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        payment = Payment.objects.get(pk=pk)
        payment_serializer = self.get_serializer(request.data)
        token = payment_serializer.data['token']
        currency = payment_serializer.data['currency']
        print('token '+token)
        print('currency '+currency)
        try:
            payment.pay(amount=payment.full_price,
                        token=token,
                        currency=currency)
        except (MissingReservation, InvalidReservation) as e:
            raise ValidationError(str(e))
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)
