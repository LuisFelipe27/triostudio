from django.contrib.auth.models import User
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from app.transversal.models import Perfil
from app.transversal.serializers import UserSerializer


class UserCreateViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer}
    )
    def create(self, request, *args, **kwargs):
        data = request.data
        user = User.objects.filter(username=data.get('username')).first()

        if user:
            serializer = self.get_serializer(user, data=data)
            status_response = status.HTTP_200_OK
        else:
            serializer = self.get_serializer(data=data)
            status_response = status.HTTP_201_CREATED

        if serializer.is_valid():
            user = serializer.save()
            if status_response == status.HTTP_200_OK:
                Perfil(usuario=user).save(set_password=False)
            return Response(serializer.data, status=status_response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
