import json

from flask_login import current_user
from sqlalchemy import Column, inspect
from sqlalchemy.orm import relationship

from services.db import db


class OlBook(db.Model):
    __tablename__ = "ol_books"
    id = Column(db.Integer, primary_key=True)

    # Data from Google Book API
    ol_id = Column(db.String(50), nullable=False)
    title = Column(db.String(100), nullable=False)
    author = Column(db.String(100), nullable=False)
    thumbnail = Column(db.String(200), nullable=True)
    description = Column(db.Text, nullable=True)
    published_year = Column(db.String(20), nullable=True)
    categories = Column(db.String(200), nullable=True)

    # Relationship with user specific data
    user_ol_books = relationship("UserOlBook", back_populates="ol_book", cascade="all, delete-orphan")

    def __repr__(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }

    def to_dict(self):
        return {
            c.key: getattr(self, c.key)
            for c in inspect(self).mapper.column_attrs
        }

    def to_json(self):
        owned = None
        status = None
        shelf_pos = None
        if current_user.is_authenticated:
            user_ol_book = current_user.get_user_ol_book(self.ol_id)
            if user_ol_book:
                owned = user_ol_book.owned
                status = user_ol_book.status.name
                shelf_pos = user_ol_book.shelf_pos
        data = {
            "ol_id": self.ol_id,
            "title": self.title,
            "author": self.author,
            "thumbnail": self.thumbnail,
            "description": self.description,
            "shelf_pos": shelf_pos,
            "owned": owned,
            "status": status,
            "published_date": self.published_year
        }
        return json.dumps(data, default=str)

    def update_from_json(self, data: dict):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self