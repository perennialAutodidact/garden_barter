from rest_framework import serializers
from .models import *

from users_app.serializers import UserDetailSerializer
class BarterSerializer(serializers.ModelSerializer):

    creator = UserDetailSerializer(read_only=True)

    class Meta:
        model = Barter
        fields = [
            "creator",
            "title",
            "description",
            "date_created",
            "date_updated",
            "date_expires",
            "postal_code",
            "latitude",
            "longitude",
            "cross_street_1",
            "cross_street_2",
            "will_trade_for",
            "is_free",
            "quantity",
            "quantity_units",
            "barter_type"
        ]



class SeedBarterSerializer(BarterSerializer):

    class Meta:
        model = SeedBarter
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'year_packaged'
        ]


class PlantBarterSerializer(BarterSerializer):
    class Meta:
        model = PlantBarter
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'age'
        ]


class ProduceBarterSerializer(BarterSerializer):
    class Meta:
        model = ProduceBarter
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
            'date_harvested'
        ]


class MaterialBarterSerializer(BarterSerializer):
    model = MaterialBarter


class ToolBarterSerializer(BarterSerializer):
    model = ToolBarter
