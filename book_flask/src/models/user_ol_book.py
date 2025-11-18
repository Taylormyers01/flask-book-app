from sqlalchemy import Enum
from sqlalchemy.orm import validates

from models.constants import BookStatus
from services.db import db


class UserOlBook(db.Model):
    __tablename__='user_ol_books'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    ol_book_id = db.Column(db.Integer, db.ForeignKey('ol_books.id'), primary_key=True)

    status = db.Column(Enum(BookStatus), default=BookStatus.NONE)
    shelf_pos = db.Column(db.Integer)
    owned = db.Column(db.Boolean)

    user = db.relationship("User", back_populates="user_ol_books")
    ol_book = db.relationship("OlBook", back_populates="user_ol_books")


    # -----------------------
    # VALIDATION HOOKS
    # -----------------------
    @validates("shelf_pos")
    def validate_shelf_pos(self, key, value):
        """Set shelf_pos only if allowed, otherwise force None."""
        if value is not None:
            if self.status != BookStatus.READ and not self.owned:
                return None
        return value

    @validates("status", "owned")
    def validate_status_or_owned(self, key, value):
        """If status or owned changes and invalidates shelf_pos, reset it."""
        future_status = value if key == "status" else self.status
        future_owned = value if key == "owned" else self.owned

        # If shelf_pos exists and in a valid status or owned
        if self.shelf_pos is not None:
            if future_status != BookStatus.READ or not future_owned:
                self.shelf_pos = None

        return value