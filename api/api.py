from django.http import Http404
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import User
from .schemas import UserSchema, CreateUserSchema, UpdateUserSchema
from datetime import datetime
import logging

router = NinjaAPI()
logger = logging.getLogger(__name__)


@router.get("/users", response={200: list[UserSchema], 500: dict})
def list_users(request):
    """List all users."""
    try:
        users = User.objects.all()
        return users
    except Exception as e:
        logger.error(f"Error while listing users: {e}")
        return 500, {"error": "An error occurred while listing users."}


@router.get("/users/{user_id}/", response={200: UserSchema, 404: dict, 500: dict})
def get_user(request, user_id: int):
    """Retrieve a user by ID."""
    try:
        user = get_object_or_404(User, id=user_id)
        return user
    except Http404:
        return 404, {"error": "User not found."}
    except Exception as e:
        logger.error(f"Error while retrieving user {user_id}: {e}")
        return 500, {"error": "An error occurred while retrieving the user."}


@router.post("/users", response={201: UserSchema, 400: dict, 500: dict})
def create_user(request, data: CreateUserSchema):
    """Create a new user with role validation."""
    if data.role.upper() not in [User.RoleTypes.ADMIN.value.upper(), User.RoleTypes.PARTICIPANT.value.upper()]:
        return 400, {"error": "Invalid role. Must be 'ADMIN' or 'PARTICIPANT'."}

    try:
        user = User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role.upper(),
            creation_date=datetime.now(),
            modification_date=datetime.now(),
        )
        return 201, user
    except IntegrityError as e:
        logger.error(f"Integrity error while creating user: {e}")
        return 400, {"error": "Username or email already exists."}
    except Exception as e:
        logger.error(f"Error while creating user: {e}")
        return 500, {"error": "An error occurred while creating the user."}


@router.put("/users/{user_id}/", response={200: UserSchema, 400: dict, 404: dict, 500: dict})
def update_user(request, user_id: int, data: UpdateUserSchema):
    """Update a user's profile and other fields."""
    try:
        user = get_object_or_404(User, id=user_id)
        for attr, value in data.dict(exclude_unset=True).items():
            setattr(user, attr, value)
        user.modification_date = datetime.now()
        user.save()
        return user
    except Http404:
        return 404, {"error": "User not found."}
    except IntegrityError as e:
        logger.error(f"Integrity error while updating user {user_id}: {e}")
        return 400, {"error": "Integrity error occurred while updating the user."}
    except Exception as e:
        logger.error(f"Error while updating user {user_id}: {e}")
        return 500, {"error": "An error occurred while updating the user."}


@router.delete("/users/{user_id}/", response={200: str, 404: dict, 500: dict})
def delete_user(request, user_id: int):
    """Delete a user."""
    try:
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return 200, "User successfully deleted."
    except Http404:
        return 404, {"error": "User not found."}
    except Exception as e:
        logger.error(f"Error while deleting user {user_id}: {e}")
        return 500, {"error": "An error occurred while deleting the user."}
