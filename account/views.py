from datetime import timedelta
import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from .serializers import SignUpSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Profile


@api_view(["POST"])
def register(request):
    data = request.data

    user = SignUpSerializer(data=data)

    if user.is_valid:
        if not User.objects.filter(username=data["email"]).exists():
            user = User.objects.create(
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                username=data["email"],
                password=make_password(data["password"])
            )

            return Response({"success": "User account created successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "User already exist."}, status=status.HTTP_400_BAD_REQUEST )

    else:
        return Response(user.errors)


@api_view(["GET"])
@permission_classes([IsAuthenticated,])
def current_user(request):
    user = UserSerializer(request.user)

    return Response(user.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    user.first_name = data["first_name"]
    user.last_name = data["last_name"]
    user.username = data["email"]
    user.email = data["email"]

    user.save()

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


def get_current_host(request):
    """Helper method for getting """
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/api/".format(protocol=protocol, host=host)


@api_view(["POST"])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, email=data["email"])

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({"error": "Profile not found"})

    token = get_random_string(40)
    expire_date = datetime.datetime.now() + timedelta(minutes=1)

    profile.reset_password_token = token
    profile.reset_password_expire = expire_date

    profile.save()

    host = get_current_host(request)
    link = "{host}/api/reset_password/{token}".format(host=host, token=token)
    body = "Your password reset link is: {link}".format(link=link)

    send_mail(
        "Password reset link for your E-Shop account",
        body,
        "no-reply@eshop.com",
        [data["email"]]
    )

    return Response({'details': 'password reset link sent to: {email}'.format(email=data['email'])})


@api_view(["POST"])
def reset_password(request, token):
    data = request.data

    user = get_object_or_404(User, profile__reset_password_token=token)

    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.datetime.now():
        return Response({"error": "Token has expired"}, status=status.HTTP_400_BAD_REQUEST)

    if data["password"] != data["confirm_password"]:
        return Response({"error": "Passwords do not match"})

    user.password = make_password(data["password"])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None

    user.profile.save()
    user.save()

    return Response({"success": "Password reset successful."})
