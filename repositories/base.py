"""Base repository with common CRUD operations."""

from typing import TypeVar, Generic, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Base repository class for CRUD operations."""

    def __init__(self, db: Session, model: type):
        self.db = db
        self.model = model

    def create(self, obj_in: dict) -> T:
        """Create a new object."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def get_by_id(self, obj_id: Any) -> Optional[T]:
        """Get object by id (excludes soft-deleted)."""
        return self.db.query(self.model).filter(
            and_(self.model.id == obj_id, self.model.deleted_at.is_(None))
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects (excludes soft-deleted)."""
        return self.db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    def update(self, obj_id: Any, obj_in: dict) -> Optional[T]:
        """Update an object."""
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return None

        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, obj_id: Any) -> bool:
        """Soft delete an object."""
        db_obj = self.get_by_id(obj_id)
        if not db_obj:
            return False

        db_obj.deleted_at = func.now()
        self.db.commit()
        return True

    def count(self) -> int:
        """Count all objects (excludes soft-deleted)."""
        return self.db.query(func.count(self.model.id)).filter(
            self.model.deleted_at.is_(None)
        ).scalar()
