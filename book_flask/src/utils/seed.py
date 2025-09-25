import os
import random

from werkzeug.security import generate_password_hash

from models.book import Book
from models.constants import BookStatus
from models.user import User
from services.book_service import test_data


class Seeder:
    def __init__(self, db):
        self.db = db

    def seed(self):
        seed = os.environ.get('SEED', 'false')
        seed = seed.lower() == 'true'
        if seed:
            print("Seeding database with test data")
            self.clear_data()
            self.add_users()
            self.add_books()
            self.db.session.commit()
            self.link_users_books()
            self.db.session.commit()
            print("✅ Database seeded successfully!")
        else:
            print("Database not flagged for seeding")


    def clear_data(self):
        # Clear in reverse dependency order
        self.db.session.query(User).delete()
        self.db.session.query(Book).delete()
        self.db.session.commit()
        print("🗑️  Old data cleared.")

    def add_users(self):
        self.user1 = User(
            username="taylor",
            password_hash=generate_password_hash("taylor")
        )
        self.user2 = User(
            username="erin",
            password_hash=generate_password_hash("erin")
        )
        self.db.session.add_all([self.user1, self.user2])
        print("👤 Users added.")

    def add_books(self):
        self.book_list = test_data()
        for book in self.book_list:
            book.owned = random.choice([True, False])
            book.status = random.choice([status for status in BookStatus])
        self.db.session.add_all(self.book_list)
        print("📚 Books added.")

    def link_users_books(self):
        for i in range(20):
            self.user1.books.add(self.book_list[i])
        for i in range(20, 40):
            self.user2.books.add(self.book_list[i])
        print("🔗 User-book relationships created.")
