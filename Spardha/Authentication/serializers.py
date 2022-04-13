from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.validators import UniqueValidator

from .models import UserAccount


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()

    class Meta:
        model = UserAccount
        fields = ("username", "password")


class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class NewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6)
    token = serializers.CharField(min_length=1, allow_blank=True, allow_null=True)
    uidb64 = serializers.CharField(min_length=1, allow_blank=True, allow_null=True)

    class Meta:
        fields = ["password", "token", "uidb64"]

    def validate(self, data):
        try:
            password = data.get("password")
            token = data.get("token")
            uidb64 = data.get("uidb64")
            id = force_str(urlsafe_base64_decode(uidb64))
            user = UserAccount.objects.get(id=id)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(password)
                user.save()
            else:
                raise AuthenticationFailed("The reset link is invalid", 401)

        except Exception:
            raise AuthenticationFailed("The reset link is invalid", 401)

        return super().validate(data)


def check(data):
    return authenticate(email=data["email"], password=data["password"])


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500)


def check_mobile_number(value):
    if len(value) == 10 and value.isdigit():
        return True
    raise ValidationError("Please enter a valid mobile number.")


class RegisterSerializer(serializers.Serializer):
    # TODO: Implement register functionality
    username = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserAccount.objects.all(),
                message=("Username already exists. Please try something new!"),
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserAccount.objects.all(),
                message=("Email is already registered with us. Please login!"),
            )
        ],
    )
    password = serializers.CharField(write_only=True, required=True)
    name = serializers.CharField(required=True)
    institution_name = serializers.CharField(
        required=True,
    )
    designation = serializers.CharField(required=True)
    phone_no = serializers.CharField(required=True, validators=[check_mobile_number])

    class Meta:
        model = UserAccount
        fields = "__all__"

    def create(self, validated_data):
        user = UserAccount.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        user.name = validated_data["name"]
        user.designation = validated_data["designation"]
        user.institution_name = validated_data["institution_name"]
        user.phone_no = validated_data["phone_no"]
        user.save()
        return user


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    institution_name = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)
    phone_no = serializers.CharField(required=True, validators=[check_mobile_number])

    class Meta:
        model = UserAccount
        fields = "__all__"

    def create(self, validated_data):
        user = UserAccount.objects.get(
            email=validated_data["email"],
        )
        user.name = validated_data["name"]
        user.designation = validated_data["designation"]
        user.institution_name = validated_data["institution_name"]
        user.phone_no = validated_data["phone_no"]
        user.save()
        return user
