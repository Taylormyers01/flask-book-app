import json

from flask import jsonify
from sqlalchemy.orm import relationship

from models.constants import BookStatus
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
    short_description = Column(db.String(200), nullable=True)
    description = Column(db.Text, nullable=True)
    page_count = Column(db.Integer, nullable=True)
    published_date = Column(db.String(20), nullable=True)
    categories = Column(db.String(200), nullable=True)
    info_link = Column(db.String(200), nullable=True)
    preview_link = Column(db.String(200), nullable=True)

    # User specific data
    shelf_pos = Column(db.Integer, nullable=True)
    owned = Column(db.Boolean, default=False)
    status = Column(Enum(BookStatus), default=BookStatus.NONE)

    # User Relationship
    user_id = Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="books")

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
        data = {
            "g_id": self.g_id,
            "title": self.title,
            "author": self.author,
            "thumbnail": self.thumbnail,
            "description": self.description,
            "shelf_pos": self.shelf_pos,
            "owned": self.owned,
            "status": self.status.name if self.status else None,
            "page_count": self.page_count,
            "published_date": self.published_date
        }

        return json.dumps(data, default=str)