from datetime import datetime, timedelta, timezone
import jwt
from nxtbn.users.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class JWTManager:
    def __init__(self):
        self.secret_key = settings.NXTBN_JWT_SETTINGS['SECRET_KEY']
        self.algorithm = settings.NXTBN_JWT_SETTINGS['ALGORITHM']
        self.access_token_expiration = settings.NXTBN_JWT_SETTINGS['ACCESS_TOKEN_EXPIRATION']
        self.refresh_token_expiration = settings.NXTBN_JWT_SETTINGS['REFRESH_TOKEN_EXPIRATION']
        self.access_token_cookie_name = settings.NXTBN_JWT_SETTINGS['ACCESS_TOKEN_COOKIE_NAME']
        self.refresh_token_cookie_name = settings.NXTBN_JWT_SETTINGS['REFRESH_TOKEN_COOKIE_NAME']

        # convert timedelta to seconds
        if isinstance(self.access_token_expiration, timedelta):
            self.access_token_expiration_seconds = int(self.access_token_expiration.total_seconds())
        else:
            self.access_token_expiration_seconds = self.access_token_expiration

        if isinstance(self.refresh_token_expiration, timedelta):
            self.refresh_token_expiration_seconds = int(self.refresh_token_expiration.total_seconds())
        else:
            self.refresh_token_expiration_seconds = self.refresh_token_expiration

    def _generate_jwt_token(self, user, expiration_timedelta):
        """Generate a JWT token for a given user with specified expiration."""
        if not user.is_active:
            raise ValueError("Inactive users cannot generate tokens.")

        if isinstance(expiration_timedelta, timedelta):
            expiration_seconds = expiration_timedelta.total_seconds()  # Convert to seconds
        else:
            expiration_seconds = expiration_timedelta

        exp = datetime.now(timezone.utc) + timedelta(seconds=expiration_seconds)
        payload = {
            "user_id": user.id,
            "exp": exp,
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def generate_access_token(self, user):
        return self._generate_jwt_token(user, self.access_token_expiration)

    def generate_refresh_token(self, user):
        return self._generate_jwt_token(user, self.refresh_token_expiration)

    def verify_jwt_token(self, token):
        """Verify a JWT token and return the associated user."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user = User.objects.get(id=payload["user_id"])
            if user.is_active:
                return user
            else:
                return None
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ObjectDoesNotExist):
            return None
        

    def revoke_refresh_token(self, token): # When you want, implement this method
        """Revoke a refresh token."""
