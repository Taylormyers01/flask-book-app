import json

from flask_login import current_user
from sqlalchemy.orm import relationship

from services.db import db
from sqlalchemy import inspect, Enum, Column, Integer


class Book(db.Model):
    __tablename__ = "books"
    id = Column(db.Integer, primary_key=True)

    # Data from Google Book API
    g_id = Column(db.String(50), nullable=False)
    title = Column(db.String(100), nullable=False)
    author = Column(db.String(100), nullable=False)
    thumbnail = Column(db.String(200), nullable=True)
    thumbnail_small = Column(db.String(200), nullable=True)
    # short_description = Column(db.String(200), nullable=True)
    description = Column(db.Text, nullable=True)
    page_count = Column(db.Integer, nullable=True)
    published_date = Column(db.String(20), nullable=True)
    categories = Column(db.String(200), nullable=True)
    # info_link = Column(db.String(200), nullable=True)
    # preview_link = Column(db.String(200), nullable=True)

    # Relationship with user specific data
    user_books = relationship("UserBook", back_populates="book", cascade="all, delete-orphan")

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
            user_book = current_user.get_user_book(self.g_id)
            if user_book:
                owned = user_book.owned
                status = user_book.status
                shelf_pos = user_book.shelf_pos
        data = {
            "g_id": self.g_id,
            "title": self.title,
            "author": self.author,
            "thumbnail": self.thumbnail,
            "description": self.description,
            "shelf_pos": shelf_pos,
            "owned": owned,
            "status": status,
            "page_count": self.page_count,
            "published_date": self.published_date
        }

        return json.dumps(data, default=str)