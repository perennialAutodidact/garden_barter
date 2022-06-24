from rest_framework import serializers
from .models import *

from users_app.serializers import UserDetailSerializer

QUANTITY_UNIT_CHOICES = dict(QUANTITY_UNIT_CHOICES)
class BarterSerializer(serializers.ModelSerializer):

    creator = UserDetailSerializer(read_only=True)

    class Meta:
        model = Barter
        fields = [
            "id",
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
        read_only_fields = ["id", "creator", "date_created", "date_updated", "date_expires", "barter_ptr"]

    def validate_is_free(self, is_free):
        if is_free == None:
            raise serializers.ValidationError('is_free cannot be null')
        if not is_free and not self.initial_data.get('will_trade_for'):
            raise serializers.ValidationError("Unless an item is free it must be traded for something. Check that the item's 'is_free' value is False.")

        return is_free

    def to_representation(self, instance):
        """Convert `username` to lowercase."""
        ret = super().to_representation(instance)
        ret['quantity_units'] = QUANTITY_UNIT_CHOICES[ret['quantity_units']]
        return ret

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
        ]


class ProduceBarterSerializer(BarterSerializer):
    class Meta:
        model = ProduceBarter
        fields = BarterSerializer.Meta.fields + [
            'genus',
            'species',
            'common_name',
        ]


class MaterialBarterSerializer(BarterSerializer):
    model = MaterialBarter


class ToolBarterSerializer(BarterSerializer):
    model = ToolBarter
