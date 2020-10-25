from dynamic_rest.viewsets import WithDynamicViewSetMixin
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from event.models import Event
from event.serializers import EventSerializer


class EventViewset(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet,
                   WithDynamicViewSetMixin):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
