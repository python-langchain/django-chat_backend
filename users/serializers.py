from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "full_name",
            "nickname",
            "role",
            "other_info",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined", "role"]  # role can be set by admins

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)

        user.set_password(password)
        user.save()

        return user


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "nickname"]
