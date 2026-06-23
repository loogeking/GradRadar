from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Favorite


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']


class FavoriteSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.name', read_only=True, default=None)
    major_name = serializers.CharField(source='major.name', read_only=True, default=None)
    major_code = serializers.CharField(source='major.code', read_only=True, default=None)
    major_college_name = serializers.CharField(source='major.college.name', read_only=True, default=None)
    major_school_name = serializers.CharField(source='major.college.school.name', read_only=True, default=None)
    major_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = [
            'id', 'target_type',
            'school', 'school_name',
            'major', 'major_name', 'major_code',
            'major_college_name', 'major_school_name', 'major_full_name',
            'note', 'created_at'
        ]
        read_only_fields = ['created_at']

    def get_major_full_name(self, obj):
        if obj.major:
            return f'{obj.major.college.school.name} - {obj.major.college.name} - {obj.major.name}'
        return None