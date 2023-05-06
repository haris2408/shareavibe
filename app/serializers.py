from rest_framework import serializers
from .models import Cafe,Address

class cafeSerializer(serializers.Serializer):
    model = Cafe
    fields = ('__all__')

class addressSerializer(serializers.Serializer):
    model = Address
    fields = ('__all__')

