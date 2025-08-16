"""
URL configuration for AI_Launch_Pad project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from launches.models import TokenLaunch, TokenCategory
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import obtain_auth_token
from core.models import Web3Nonce, User
import secrets
from eth_account.messages import encode_defunct
from eth_account.account import Account


@api_view(["GET"])  # DRF view, but explicitly disable throttling for health
@permission_classes([AllowAny])
@throttle_classes([])
def health(_request):
    return Response({"status": "ok", "time": timezone.now()})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def launches(request):
    if request.method == "POST":
        data = request.data
        # Ensure we have a valid category; fallback to a default if not provided
        category_id = data.get("category_id")
        if not category_id:
            default_cat, _ = TokenCategory.objects.get_or_create(
                slug="general",
                defaults={
                    "name": "General",
                    "description": "General token launches",
                    "is_active": True,
                },
            )
            category_id = str(default_cat.id)
        launch = TokenLaunch.objects.create(
            creator=request.user,
            name=data.get("name", ""),
            symbol=data.get("symbol", ""),
            description=data.get("description", ""),
            category_id=category_id,
            network=data.get("network", "ETHEREUM"),
            total_supply=data.get("total_supply", 0),
        )
        return Response({"id": str(launch.id)}, status=201)
    qs = TokenLaunch.objects.all().values(
        "id",
        "name",
        "symbol",
        "status",
        "network",
        "contract_address",
        "created_at",
    )
    return Response(list(qs))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def attach_tx(request, launch_id: str):
    tx = request.data.get("tx_hash")
    addr = request.data.get("contract_address")
    try:
        launch = TokenLaunch.objects.get(id=launch_id, creator=request.user)
    except TokenLaunch.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
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


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("api/auth/token/", obtain_auth_token),
    path("api/launches/", launches),
    path("api/launches/<uuid:launch_id>/attach_tx/", attach_tx),
]


@api_view(["POST"])
@permission_classes([AllowAny])
def web3_get_nonce(request):
    address = (request.data.get("address") or "").strip().lower()
    if not address.startswith("0x") or len(address) != 42:
        return Response({"detail": "invalid address"}, status=400)
    nonce = secrets.token_hex(16)
    Web3Nonce.objects.update_or_create(address=address, defaults={"nonce": nonce})
    return Response({"nonce": nonce})


@api_view(["POST"])
@permission_classes([AllowAny])
def web3_verify(request):
    address = (request.data.get("address") or "").strip().lower()
    signature = request.data.get("signature")
    if not address or not signature:
        return Response({"detail": "address and signature required"}, status=400)
    try:
        rec = Web3Nonce.objects.get(address=address)
    except Web3Nonce.DoesNotExist:
        return Response({"detail": "nonce not found"}, status=400)
    message = encode_defunct(text=f"AI-Launch-Pad login: {rec.nonce}")
    try:
        recovered = Account.recover_message(message, signature=signature)
    except Exception:
        return Response({"detail": "invalid signature"}, status=400)
    if recovered.lower() != address:
        return Response({"detail": "address mismatch"}, status=400)
    # Get or create user by wallet address
    user, _ = User.objects.get_or_create(
        username=address, defaults={"wallet_address": address}
    )
    if not user.wallet_address:
        user.wallet_address = address
        user.save(update_fields=["wallet_address"])
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=user)
    rec.delete()
    return Response({"token": token.key})


urlpatterns += [
    path("api/auth/web3/nonce/", web3_get_nonce),
    path("api/auth/web3/verify/", web3_verify),
]
