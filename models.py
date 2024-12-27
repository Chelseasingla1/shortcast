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
    access_token: Mapped[str] = mapped_column()
    profile_image_url: Mapped[str] = mapped_column()
    podcast: Mapped[List['Podcast']] = relationship('Podcast', back_populates='user')

class Podcast(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    title: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column()
    user: Mapped[User] = relationship('User', back_populates='streams')

# TODO : filter by , title,user,posted
