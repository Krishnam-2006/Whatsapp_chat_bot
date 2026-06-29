from sqlalchemy.orm import Session
from app.models.user import User


def get_user(db: Session, whatsapp_number: str):
    return db.query(User).filter(User.whatsapp_number == whatsapp_number).first()


def create_user(db: Session, whatsapp_number: str):
    db_user = User(whatsapp_number=whatsapp_number)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, whatsapp_number: str, **kwargs):
    db_user = db.query(User).filter(User.whatsapp_number == whatsapp_number).first()

    if db_user:
        for key, value in kwargs.items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)

    return db_user
