from rest_framework import serializers
from .models import *

class BarterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barter
        fields = [
            'creator',
            'title',
            'description',
            'will_trade_for',
            'is_free'
        ]

class SeedSerializer(BarterSerializer):
    class Meta:
        model = Seed
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'date_packaged'
        ]

class PlantSerializer(BarterSerializer):
    class Meta:
        model = Plant
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'age'
        ]

class ProduceSerializer(BarterSerializer):
    class Meta:
        model = Produce
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'date_harvested'
        ]


class MaterialSerializer(BarterSerializer):
    model = Material

class ToolSerializer(BarterSerializer):
    model = Tool