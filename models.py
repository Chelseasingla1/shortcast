from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, ForeignKey, LargeBinary
from typing import List
from flask_login import UserMixin


class Base(DeclarativeBase):
    ...


db = SQLAlchemy(model_class=Base)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    username: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    # token_data: Mapped[str] = mapped_column()
    profile_image_url: Mapped[str] = mapped_column()
    # streams: Mapped[List['Stream']] = relationship('Stream', back_populates='user')
