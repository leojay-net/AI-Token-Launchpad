from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import TokenLaunch
from .serializers import TokenLaunchSerializer


class TokenLaunchViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TokenLaunch.objects.all().order_by("-created_at")
    serializer_class = TokenLaunchSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"], url_path="attach_tx")
    def attach_tx(self, request, pk=None):
        launch = self.get_object()
        tx = request.data.get("tx_hash")
        addr = request.data.get("contract_address")
        if addr:
            launch.contract_address = addr
        launch.status = "LIVE"
        launch.launched_at = timezone.now()
        launch.save(update_fields=["contract_address", "status", "launched_at"])
        return Response(
            {
                "id": str(launch.id),
                "tx_hash": tx,
                "contract_address": launch.contract_address,
            }
        )
