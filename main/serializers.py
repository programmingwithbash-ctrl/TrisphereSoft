from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import User, Attendace, Catalog, Circulation, Acquisition, Duty, Message
from django.contrib.auth.models import Permission, Group

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["id", "name", "codename", "content_type"]


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source="permissions"
    )

    class Meta:
        model = Group
        fields = ["id", "name", "permissions", "permission_ids"]


class UserCreateSerializer(BaseUserCreateSerializer):

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            "id", "first_name", "last_name", "username", "email", "password",
            "phone", "student_id", "faculty", "department", "student_category",

        ]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            "id", "first_name", "last_name", "username", "email",
            "phone", "student_id", "faculty", "department", "student_category",
            "is_active", "is_staff", "is_superuser", "password",
        ]


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class AttendaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendace
        fields = [
            'id', 'user', 'fingerprint_data', 'reg_no', 'name', 'category', 'faculty', 'department', 'items', 'purpose', 'method', 'check_out', 'created_at', 'updated_at'
        ]


class CatalogSerializer(serializers.ModelSerializer):
    added_by = UserNestedSerializer(read_only=True)
    class Meta:
        model = Catalog
        fields = [
            'id', 'title', 'marc_tag', 'dublin_core', 'ai_suggestion', 'isbn', 'issn', 'lccn', 'dewey_decimal',
            'subject', 'language', 'format', 'publisher', 'year', 'contributors', 'notes', 'tags', 'quantity', 'can_be_borrowed', 'created_at', 'updated_at', 'added_by'
        ]

class CirculationSerializer(serializers.ModelSerializer):
    book = CatalogSerializer(read_only=True)
    student_name = serializers.CharField(required=False, allow_blank=True)
    student_card_id = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        book = data.get('book')
        status = data.get('status')
        if status == 'borrowed':
            if not book.can_be_borrowed:
                raise serializers.ValidationError({'book': 'This item cannot be borrowed.'})
            from main.models import Circulation
            borrowed_status = ['borrowed', 'overdue']
            borrowed_count = Circulation.objects.filter(book=book, status__in=borrowed_status).count()
            available = book.quantity - borrowed_count
            if available <= 0:
                raise serializers.ValidationError({'book': 'No available copies to borrow.'})
        return data

    class Meta:
        model = Circulation
        fields = [
            'id', 'book', 'student_name', 'student_card_id', 'borrow_date', 'return_date', 'actual_return', 'fine', 'status'
        ]

class AcquisitionSerializer(serializers.ModelSerializer):
    added_by = UserNestedSerializer(read_only=True)
    class Meta:
        model = Acquisition
        fields = [
            'id', 'title', 'source', 'supplier', 'amount', 'date_acquired', 'added_by'
        ]

class DutySerializer(serializers.ModelSerializer):
    class Meta:
        model = Duty
        fields = [
            'id', 'user', 'date', 'shift', 'notes'
        ]

class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'sent_at']  # 'read' field commented out
        read_only_fields = ['id', 'sent_at']

    def create(self, validated_data):
        # Automatically set sender from context (request.user)
        request = self.context.get('request')
        validated_data['sender'] = request.user
        return super().create(validated_data)

