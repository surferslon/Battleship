from django.contrib.auth import login
from django.contrib.auth.models import User
from rest_framework import permissions, status, views
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from users.serializers import LoginSerializer, UserSerializer


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=self.request.data, context={"request": self.request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        return Response(None, status=status.HTTP_202_ACCEPTED)
