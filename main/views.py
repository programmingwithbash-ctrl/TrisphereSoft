from django.contrib.auth.models import Permission, Group
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from .models import (Attendance, Catalog, Circulation, 
                     Acquisition, Duty, Message
                     )
from .serializers import (
    AttendanceSerializer, CatalogSerializer, CirculationSerializer, 
    AcquisitionSerializer, DutySerializer, MessageSerializer,
    PermissionSerializer, GroupSerializer
)
from .permissions import AttendancePermission, MessagePermission, FullDjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import User
from rest_framework import status
from .serializers import UserSerializer
from django.db import models
from django.utils.timezone import now, timedelta


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()
    permission_classes = [AttendancePermission]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff or user.has_perm('main.can_manage_attendance'):
            return Attendance.objects.all()

        return Attendance.objects.filter(user=user)
    

    def create(self, request, *args, **kwargs):
        barcode = request.data.get("barcode")

        if not barcode:
            return Response({"detail": "Barcode is required"}, status=400)

        # Find user by barcode
        try:
            user = User.objects.get(barcode=barcode)
        except User.DoesNotExist:
            return Response({"detail": "No user found with this barcode"}, status=404)

        # Prevent duplicates
        time_limit = now() - timedelta(minutes=1)
        existing = Attendance.objects.filter(
            user=user,
            created_at__gte=time_limit
        ).first()

        if existing:
            serializer = self.get_serializer(existing)
            return Response({
                "detail": "Attendance already recorded recently",
                "attendance": serializer.data,
                "user_data": self.get_user_data(user),
            }, status=200)

        serializer = self.get_serializer(
            data=request.data,
            context={"user": user}
        )
        serializer.is_valid(raise_exception=True)
        attendance = serializer.save()

        return Response({
            **serializer.data,
            "user_data": self.get_user_data(user)
        }, status=status.HTTP_201_CREATED)


    def get_user_data(self, user):
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "faculty": user.faculty,
            "department": user.department,
            "category": user.user_category or user.staff_category
        }



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
                "role": "admin" if user.is_superuser else ("staff" if user.is_staff else (user.staff_category or user.user_category or "user")),
            })
        return Response(data, status=status.HTTP_200_OK)
    

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]