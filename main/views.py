from django.contrib.auth.models import Permission, Group
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from .models import (Attendace, Catalog, Circulation, 
                     Acquisition, Duty, Message
                     )
from .serializers import (
    AttendaceSerializer, CatalogSerializer, CirculationSerializer, 
    AcquisitionSerializer, DutySerializer, MessageSerializer,
    PermissionSerializer, GroupSerializer
)
from .permissions import AttendacePermission, MessagePermission, FullDjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from rest_framework import status
from .serializers import UserSerializer
from django.db import models


class AttendaceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendaceSerializer
    permission_classes = [AttendacePermission]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.has_perm('main.can_manage_attendance'):
            return Attendace.objects.all()
        return Attendace.objects.filter(user=user)

class CatalogViewSet(viewsets.ModelViewSet):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    permission_classes = [FullDjangoModelPermissions]

class CirculationViewSet(viewsets.ModelViewSet):
    queryset = Circulation.objects.all()
    serializer_class = CirculationSerializer
    permission_classes = [FullDjangoModelPermissions]

class AcquisitionViewSet(viewsets.ModelViewSet):
    queryset = Acquisition.objects.all()
    serializer_class = AcquisitionSerializer
    permission_classes = [FullDjangoModelPermissions]

class DutyViewSet(viewsets.ModelViewSet):
    queryset = Duty.objects.all()
    serializer_class = DutySerializer
    permission_classes = [FullDjangoModelPermissions]

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [MessagePermission]

    def get_queryset(self):
        queryset = super().get_queryset()
        user1_id = self.request.query_params.get('user1_id')
        user2_id = self.request.query_params.get('user2_id')
        read = self.request.query_params.get('read')
        if user1_id and user2_id:
            queryset = queryset.filter(
                (
                    models.Q(sender_id=user1_id, receiver_id=user2_id) |
                    models.Q(sender_id=user2_id, receiver_id=user1_id)
                )
            )
        elif user1_id:
            queryset = queryset.filter(sender_id=user1_id) | queryset.filter(receiver_id=user1_id)
        elif user2_id:
            queryset = queryset.filter(sender_id=user2_id) | queryset.filter(receiver_id=user2_id)
        if read is not None:
            queryset = queryset.filter(read=(read.lower() == "true"))
        return queryset


class PermissionView(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = PermissionSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]   # only admin users can manage groups


class PublicUserListViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        users = User.objects.filter(is_active=True)
        data = []
        for user in users:
            data.append({
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": "admin" if user.is_superuser else ("staff" if user.is_staff else (user.staff_category or user.student_category or "user")),
            })
        return Response(data, status=status.HTTP_200_OK)