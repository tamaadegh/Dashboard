from django.db import IntegrityError
import graphene
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _


from django.conf import settings
from django.contrib.auth import get_user_model

from nxtbn.users.api.storefront.serializers import JwtBasicUserSerializer
from nxtbn.users.utils.jwt_utils import JWTManager
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings


class TokenType(graphene.ObjectType):
    access = graphene.String()
    refresh = graphene.String()
    expiresIn = graphene.Int()
    refreshExpiresIn = graphene.Int()

class UserType(graphene.ObjectType):
    id = graphene.ID()
    email = graphene.String()
    username = graphene.String()
    firstName = graphene.String()
    lastName = graphene.String()
    full_name = graphene.String()
    role = graphene.String()

class LoginResponse(graphene.ObjectType):
    user = graphene.Field(UserType)
    storeUrl = graphene.String()
    version = graphene.String()
    token = graphene.Field(TokenType)

class SignupResponse(graphene.ObjectType):
    user = graphene.Field(UserType)
    token = graphene.Field(TokenType)

class CustomerSignupMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)

    signup = graphene.Field(SignupResponse)

    def mutate(self, info, email, password, username, first_name, last_name):
        jwt_manager = JWTManager()

        # Create the user
        try:
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_staff=False,
                is_superuser=False,
            )
        except IntegrityError:
            raise Exception(_("User with this email already exists."))

        # Send the verification email
        complete_signup(info.context, user, allauth_settings.EMAIL_VERIFICATION, None)

        response_data = {"detail": _("Verification e-mail sent. Please check your email.")}

        # If email verification is not mandatory, generate access and refresh tokens
        if allauth_settings.EMAIL_VERIFICATION != allauth_settings.EmailVerificationMethod.MANDATORY:
            access_token = jwt_manager.generate_access_token(user)
            refresh_token = jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data
            response_data = {
                "user": user_data,
                "token": {
                    "access": access_token,
                    "refresh": refresh_token,
                    "expiresIn": jwt_manager.access_token_expiration_seconds,
                    "refreshExpiresIn": jwt_manager.refresh_token_expiration_seconds,
                },
            }

        return CustomerSignupMutation(signup=SignupResponse(**response_data))

class CustomerLoginMutation(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    login = graphene.Field(LoginResponse)

    def mutate(self, info, email, password):
        jwt_manager = JWTManager()

        user = authenticate(email=email, password=password)
        if user:
            if user.is_staff:
                raise Exception("Internal staff members cannot log in.")
            
            if not user.is_active:
                raise Exception("User is not active.")

            access_token = jwt_manager.generate_access_token(user)
            refresh_token = jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data

            response = LoginResponse(
                user=UserType(**user_data),
                storeUrl=settings.STORE_URL,
                version=settings.VERSION,
                token=TokenType(
                    access=access_token,
                    refresh=refresh_token,
                    expiresIn=jwt_manager.access_token_expiration_seconds,
                    refreshExpiresIn=jwt_manager.refresh_token_expiration_seconds
                )
            )

            return CustomerLoginMutation(login=response)
        else:
            raise Exception("Invalid credentials")
        



class TokenRefreshMutation(graphene.Mutation):
    class Arguments:
        refresh_token = graphene.String(required=True)

    refresh = graphene.Field(LoginResponse)

    def mutate(self, info, refresh_token):
        jwt_manager = JWTManager()

        # Verify refresh token
        user = jwt_manager.verify_jwt_token(refresh_token)

        if user:
            access_token = jwt_manager.generate_access_token(user)
            new_refresh_token = jwt_manager.generate_refresh_token(user)

            user_data = JwtBasicUserSerializer(user).data

            response = LoginResponse(
                user=UserType(**user_data),
                storeUrl=settings.STORE_URL,
                version=settings.VERSION,
                token=TokenType(
                    access=access_token,
                    refresh=new_refresh_token,
                    expiresIn=jwt_manager.access_token_expiration_seconds,
                    refreshExpiresIn=jwt_manager.refresh_token_expiration_seconds
                )
            )

            return TokenRefreshMutation(refresh=response)
        else:
            raise Exception("Invalid or expired refresh token")

class UserMutation(graphene.ObjectType):
    login = CustomerLoginMutation.Field()
    signup = CustomerSignupMutation.Field()
    refresh_token = TokenRefreshMutation.Field()
