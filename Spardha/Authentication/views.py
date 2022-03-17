from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from .serializers import (
    ResetPasswordEmailSerializer,
    NewPasswordSerializer,
    RegisterSerializer,
    check,
    LoginSerializer,
    UserSerializer,
)
from .models import UserAccount
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import (
    smart_str,
    smart_bytes,
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.urls import reverse
from .utils import Util
from rest_framework.authtoken.models import Token
from django.shortcuts import redirect
from django.http import Http404
from Spardha.settings import BASE_URL_FRONTEND


class LoginView(generics.GenericAPIView):
    """
    Implement login functionality, taking email and password
    as input, and returning the Token.
    """

    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is None or password is None:
            return Response(
                {"error": "Please provide both username and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"error": "Please check your credentials...cannot login!"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        elif user.is_active is False:
            return Response(
                {"error": "Please verify your email first and then login."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        login(request, user)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


class LogoutView(generics.GenericAPIView):
    """
    TODO:
    Implement logout functionality, logout the user.
    """

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LoginSerializer

    def get(self, request):
        request.user.auth_token.delete()
        logout(request)

        return Response(status=status.HTTP_200_OK)


def create_auth_token(user):
    """
    Returns the token required for authentication for a user.
    """
    token, _ = Token.objects.get_or_create(user=user)
    return token


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):

        email = request.data["email"]

        if UserAccount.objects.filter(email=email).exists():
            user = UserAccount.objects.get(email=email)
            if not user.is_active:
                return Response(
                    {"error": "User not authorized!"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            absurl = "http://" + current_site + relativeLink
            email_body = f"""<h2> Spardha'22 </h2>
                 <br> <strong> Hello {user.name}! </strong>
                 <br> We have received a request to reset the password of your Spardha account. <br>
                 Click the link below to proceed further: <br> <a href='{absurl}'>Reset</a> <br>
                 If you have any questions, please contact us at 
                 <a href='mailto:spardha@gmail.com'>spardha@gmail.com</a>"""
            data = {
                "email_body": email_body,
                "to_mail": [user.email],
                "email_subject": "Reset Your Spardha Password",
            }
            Util.send_email(data)
            return Response(
                {"success": "Link has been sent by email to reset password"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "No user with this email id exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )


def PasswordTokenCheck(request, uidb64, token):
    id = smart_str(urlsafe_base64_decode(uidb64))
    user = UserAccount.objects.get(id=id)
    if not PasswordResetTokenGenerator().check_token(user, token):
        raise Http404
    url = BASE_URL_FRONTEND + "/resetpage?id=" + str(uidb64) + "&token=" + str(token)
    return redirect(url)


class NewPasswordView(generics.GenericAPIView):
    serializer_class = NewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"success": True, "message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )


class UserUpdateView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserAccount.objects.all()
    serializer_class = UserSerializer

    def get(self, request):
        try:
            user = request.user
            content = {
                "name": user.name,
                "email": user.email,
                "institution": user.institution_name,
                "designation": user.designation,
                "phone": user.phone_no,
            }
            return Response(content, status=status.HTTP_200_OK)
        except serializers.get_error_detail:
            return Response(
                {"error": "An error occurred!"}, status=status.HTTP_403_FORBIDDEN
            )

    def post(self, request):
        user = UserAccount.objects.filter(email=request.user.email)
        if user is not None:
            if "name" in request.data:
                user.update(name=request.data["name"])
            if "designation" in request.data:
                user.update(
                    year=request.data["designation"],
                )
            if "institution_name" in request.data:
                user.update(
                    institution_name=request.data["institution_name"],
                )
            return Response(
                {"message": "Updated successfully!"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": "An error occurred!"}, status=status.HTTP_403_FORBIDDEN
            )
def send_verification_mail(user,request):
    uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
    token = PasswordResetTokenGenerator().make_token(user)
    current_site = get_current_site(request=request).domain
    relativeLink = reverse(
        "activate-account", kwargs={"uidb64": uidb64, "token": token}
    )
    absurl = "http://" + current_site + relativeLink
    email_body = f"""<h2> Spardha'22 </h2>
         <br> <strong> Hello {user.name}! </strong>
         <br> Thanks for registering on Spardha <br>
         To complete your sign up, we just need to verify your email address.<br>
         Click the link below to verify: <br> <a href='{absurl}'>Verify</a> <br>
         <br> If you have any questions, please contact us at 
         <a href='mailto:spardha@gmail.com'>spardha@gmail.com</a>"""
    data = {
        "email_body": email_body,
        "to_mail": [user.email],
        "email_subject": "Activate Your Spardha Account",
    }
    Util.send_email(data)

class RegisterView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = check(request.data)
            if user is None:
                user = serializer.save()
                create_auth_token(user=user)
                send_verification_mail(user,request)
                return Response(
                    {"success": "Verification link has been sent by email!"},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "User with same credentials already exists!"},
                    status=status.HTTP_226_IM_USED,
                )
        else:
            error = {}
            for err in serializer.errors:
                error[err] = serializer.errors[err][0]
            return Response(error, status=status.HTTP_409_CONFLICT)


def ActivateAccount(request, uidb64, token):
    id = smart_str(urlsafe_base64_decode(uidb64))
    user = UserAccount.objects.get(id=id)
    if not PasswordResetTokenGenerator().check_token(user, token):
        raise Http404
    url = BASE_URL_FRONTEND + "/login"
    user.is_active = True
    user.save()
    return redirect(url)

class ResendLinkView(generics.GenericAPIView):
    queryset = UserAccount.objects.all()
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request):
        try:
            user = self.queryset.get(email=request.data["email"])
            if user.is_active:
                return Response(
                    {"success": "Account already activated"},
                    status=status.HTTP_200_OK,
                )
            send_verification_mail(user,request)
            return Response(
                {"success": "Verification link has been sent on email!"},
                status=status.HTTP_200_OK,
            )
        except UserAccount.DoesNotExist:
            return Response(
                {"error": "Account with this mail is not registered!"}, status=status.HTTP_403_FORBIDDEN
            )