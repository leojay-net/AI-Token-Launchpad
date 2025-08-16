from rest_framework import serializers
from .models import TokenLaunch


class TokenLaunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenLaunch
        fields = [
            "id",
            "name",
            "symbol",
            "status",
            "network",
            "contract_address",
            "created_at",
            "category",
            "description",
            "total_supply",
        ]
