from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer, PublicUserSerializer

# Create your views here.
User = get_user_model()


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        return Response(
            PublicUserSerializer(user).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_users(request):
    q = request.query_params.get("q")
    qs = User.objects.all().order_by("id")
    if q:
        qs = (
            qs.filter(full_name__icontains=q)
            | qs.filter(nickname__icontains=q)
            | qs.filter(email__icontains=q)
        )
    return Response(PublicUserSerializer(qs, many=True).data)
