from django.http import Http404
from ninja import NinjaAPI
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from .models import User
from .schemas import UserSchema, CreateUserSchema, UpdateUserSchema
from datetime import datetime
import logging
from ninja import Query
from django.core.paginator import Paginator, EmptyPage
from typing import Optional
from ninja.decorators import decorate_view
from django.views.decorators.cache import cache_page

router = NinjaAPI(urls_namespace="users")
logger = logging.getLogger(__name__)


@router.get("/", response={200: list[UserSchema], 500: dict})
@decorate_view(cache_page(60*15))
def list_users(
    request,
    search: Optional[str] = Query(None),
    order: Optional[str] = Query(None),
    page: int = Query(1),
    page_size: int = Query(10),
):
    """
    List all users with optional search, sorting, and pagination.
    """
    try:
        users = User.objects.all()

        if search:
            users = users.filter(username__icontains=search)

        if order:
            valid_order_fields = ["username", "email",
                                  "role", "-username", "-email", "-role"]
            if order in valid_order_fields:
                users = users.order_by(order)
            else:
                return 400, {"error": f"Invalid order field. Allowed: {', '.join(valid_order_fields)}"}

        paginator = Paginator(users, page_size)
        try:
            paginated_users = paginator.page(page)
        except EmptyPage:
            return 400, {"error": "Page number out of range."}

        return [UserSchema.from_orm(user) for user in paginated_users]
    except Exception as e:
        logger.error(f"Error while listing users: {e}")
        return 500, {"error": "An error occurred while listing users."}


@router.get("/{user_id}/", response={200: UserSchema, 404: dict, 500: dict})
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


@router.post("/", response={201: UserSchema, 400: dict, 500: dict})
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


@router.put("/{user_id}/", response={200: UserSchema, 400: dict, 404: dict, 500: dict})
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


@router.delete("/{user_id}/", response={200: str, 404: dict, 500: dict})
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
