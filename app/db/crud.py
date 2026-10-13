from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


def get_user(db: Session, whatsapp_number: str):
    return db.query(User).filter(User.whatsapp_number == whatsapp_number).first()


def create_user(db: Session, whatsapp_number: str):
    db_user = User(whatsapp_number=whatsapp_number)
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        existing_user = get_user(db, whatsapp_number)

        if existing_user:
            return existing_user

        raise
    except Exception:
        db.rollback()
        raise


def update_user(db: Session, whatsapp_number: str, **kwargs):
    allowed_fields = {"state", "diet_type", "taste_preference"}

    invalid_fields = set(kwargs) - allowed_fields
    if invalid_fields:
        raise ValueError(f"Invalid user fields: {invalid_fields}")

    db_user = get_user(db, whatsapp_number)

    if db_user:
        for key, value in kwargs.items():
            setattr(db_user, key, value)

        try:
            db.commit()
            db.refresh(db_user)
        except Exception:
            db.rollback()
            raise

    return db_user

    return db_user
