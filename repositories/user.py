"""User repository."""

from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """User repository."""

    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(
            and_(User.email == email, User.deleted_at.is_(None))
        ).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(
            and_(User.username == username, User.deleted_at.is_(None))
        ).first()

    def email_exists(self, email: str) -> bool:
        """Check if email exists."""
        return self.db.query(User).filter(
            and_(User.email == email, User.deleted_at.is_(None))
        ).first() is not None

    def username_exists(self, username: str) -> bool:
        """Check if username exists."""
        return self.db.query(User).filter(
            and_(User.username == username, User.deleted_at.is_(None))
        ).first() is not None
