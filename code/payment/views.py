from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from payment.exceptions import MissingReservation, InvalidReservation
from payment.serializers import PaymentSerializer, PaymentCreationSerializer
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
        return self.serializer_class

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(client=user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        payment = Payment.objects.get(pk=pk)
        token = request.get('token')
        if not token:
            raise ValidationError('Token not included')
        try:
            payment.pay(amount=payment.full_price, token=token, currency='EUR')
        except (MissingReservation, InvalidReservation) as e:
            raise ValidationError(str(e))
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
