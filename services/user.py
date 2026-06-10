"""User service."""

from datetime import datetime
from sqlalchemy.orm import Session

from app.models import User
from app.repositories import UserRepository
from app.core import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    validate_password,
    UnauthorizedException,
    ValidationException,
    ConflictException,
)


class UserService:
    """User service."""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def register(self, email: str, username: str, password: str, **kwargs) -> User:
        """Register a new user."""
        # Validate password
        valid, message = validate_password(password)
        if not valid:
            raise ValidationException(message)

        # Check if email exists
        if self.repository.email_exists(email):
            raise ConflictException("Email already registered")

        # Check if username exists
        if self.repository.username_exists(username):
            raise ConflictException("Username already taken")

        # Create user
        user_data = {
            "email": email,
            "username": username,
            "password_hash": hash_password(password),
            **kwargs,
        }

        user = self.repository.create(user_data)

        from app.services.company import CompanyService

        company_name = kwargs.get("business_name") or f"{username} Transport"
        CompanyService(self.db).create_default_for_user(user, company_name)
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> tuple[User, dict]:
        """Login user and return tokens."""
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("User account is inactive")

        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()

        # Create tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "company_id": str(user.active_company_id) if user.active_company_id else None,
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return user, {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes
        }

    def get_by_id(self, user_id: str) -> User:
        """Get user by id."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")
        return user

    def update_profile(self, user_id: str, update_data: dict) -> User:
        """Update user profile."""
        user = self.get_by_id(user_id)
        
        updated_user = self.repository.update(user_id, update_data)
        if not updated_user:
            raise UnauthorizedException("Failed to update user")

        return updated_user

    def change_password(self, user_id: str, old_password: str, new_password: str) -> User:
        """Change user password."""
        user = self.get_by_id(user_id)

        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise UnauthorizedException("Invalid password")

        # Validate new password
        valid, message = validate_password(new_password)
        if not valid:
            raise ValidationException(message)

        # Update password
        user.password_hash = hash_password(new_password)
        self.db.commit()
        self.db.refresh(user)

        return user
