from rest_framework import serializers
from djoser.serializers import UserSerializer as BaseUserSerializer, UserCreateSerializer as BaseUserCreateSerializer
from .models import User, Attendance, Catalog, Circulation, Acquisition, Duty, Message
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
            "phone", "student_id", "faculty", "department", "user_category", 
            "staff_category"
        ]


class UserSerializer(BaseUserSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.PrimaryKeyRelatedField(      
        many=True,
        queryset=Group.objects.all(),
        write_only=True,
        source="groups"
    )
    permissions = PermissionSerializer(source="user_permissions", many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField( 
        many=True,
        queryset=Permission.objects.all(),
        write_only=True,
        source="user_permissions"
    )
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = [
            "id", "first_name", "last_name", "username", "email",
            "phone", "student_id", "faculty", "department", "user_category",
            "staff_category", "role", 'barcode', 'permissions', 'permission_ids', 'groups', 'group_ids',
            "is_active", "is_staff", "is_superuser", "password",
        ]


class UserNestedSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "user_category", "staff_category", "barcode", "faculty", "department"]

class AttendanceSerializer(serializers.ModelSerializer):
    barcode = serializers.CharField(write_only=True, required=False)
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'barcode',
            'user',
            'purpose',
            'items',
            'method',
            'sign_type',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'method', 'user']

    def create(self, validated_data):
        validated_data.pop('barcode', None)
        
        # Inject user passed from viewset
        validated_data['user'] = self.context['user']

        return super().create(validated_data)



class CatalogSerializer(serializers.ModelSerializer):
    added_by = UserNestedSerializer(read_only=True)
    class Meta:
        model = Catalog
        fields = [
            'id', 'title', 'author', 'barcode', 'marc_tag', 'dublin_core', 'ai_suggestion', 'isbn', 'issn', 'lccn', 'dewey_decimal',
            'subject', 'language', 'format', 'publisher', 'year', 'contributors', 'notes', 'tags', 'quantity', 'can_be_borrowed', 'created_at', 'updated_at', 'added_by'
        ]
class CirculationSerializer(serializers.ModelSerializer):
    user_barcode = serializers.CharField(write_only=True, required=True)
    book_barcode = serializers.CharField(write_only=True, required=True)

    borrower = UserNestedSerializer(read_only=True)

    class Meta:
        model = Circulation
        fields = [
            'id',
            'user_barcode',
            'book_barcode',
            'borrower',
            'book',
            'borrow_date',
            'return_date',
            'actual_return',
            'fine',
            'status'
        ]
        read_only_fields = ['id', 'borrower', 'book']

    def validate(self, data):
        user_barcode = data.get('user_barcode')
        book_barcode = data.get('book_barcode')
        status = data.get('status')


        # Fetch User
        try:
            self.user_instance = User.objects.get(barcode=user_barcode)
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_barcode": "User not found."})

        # Fetch Book
        try:
            self.book_instance = Catalog.objects.get(barcode=book_barcode)
        except Catalog.DoesNotExist:
            raise serializers.ValidationError({"book_barcode": "Book not found."})

        book = self.book_instance

        # Borrow validation
        if status == 'borrowed':
            if not book.can_be_borrowed:
                raise serializers.ValidationError({'book': 'This item cannot be borrowed.'})

            from main.models import Circulation
            borrowed_status = ['borrowed', 'overdue']

            borrowed_count = Circulation.objects.filter(
                book=book,
                status__in=borrowed_status
            ).count()

            available = book.quantity - borrowed_count
            if available <= 0:
                raise serializers.ValidationError({'book': 'No available copies to borrow.'})

        return data

    def create(self, validated_data):
        # Remove barcodes (not fields in model)
        validated_data.pop('user_barcode')
        validated_data.pop('book_barcode')

        return Circulation.objects.create(
            borrower=self.user_instance,
            book=self.book_instance,
            **validated_data
        )

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

