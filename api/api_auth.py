from ninja import NinjaAPI
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from ninja import Schema

router = NinjaAPI(urls_namespace="auth")


class TokenSchema(Schema):
    access: str
    refresh: str


class AuthSchema(Schema):
    username: str
    password: str


class RefreshTokenSchema(Schema):
    refresh: str


@router.post("/login", response={200: TokenSchema, 401: dict})
def login(request, data: AuthSchema):
    """
    Authenticate user and return JWT tokens
    """
    user = authenticate(username=data.username, password=data.password)
    if user:
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    return 401, {"error": "Invalid username or password"}


@router.post("/refresh", response={200: TokenSchema, 401: dict})
def refresh_token(request, data: RefreshTokenSchema):
    """
    Refresh access token using refresh token
    """
    try:
        refresh = RefreshToken(data.refresh)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
    except Exception as e:
        return 401, {"error": "Invalid or expired refresh token"}
