from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from services.db import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

book_user = Table(
    "book_user",
    db.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True)
)

class User(UserMixin, db.Model):
    __tablename__='users'
    id = Column(db.Integer, primary_key=True)
    username = Column(db.String(80), unique=True, nullable=False)
    password_hash = Column(db.String(128), nullable=False)
    books = relationship("Book", secondary=book_user, collection_class=set, back_populates="users")


    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)