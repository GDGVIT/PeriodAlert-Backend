from rest_framework import serializers
from app.models import User, Chat

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'phone_no', 'date_of_birth', 'password')

class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'password')

class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = "__all__"