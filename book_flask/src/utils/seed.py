import os
import random

from werkzeug.security import generate_password_hash

from models.constants import BookStatus
from models.ol_book import OlBook
from models.user import User
from models.user_ol_book import UserOlBook


class Seeder:
    def __init__(self, db):
        self.db = db
        self.user1 = None
        self.user2 = None
        self.book_list = []

    def seed(self):
        seed = os.environ.get('SEED', 'false')
        seed = seed.lower() == 'true'
        if seed:
            print("Seeding database with test data")
            self.clear_data()
            self.add_users()
            # self.add_books()
            self.db.session.commit()
            print("✅ Database seeded successfully!")
        else:
            print("Database not flagged for seeding")


    def clear_data(self):
        # Clear in reverse dependency order
        self.db.session.query(User).delete()
        # self.db.session.query(OlBook).delete()
        # self.db.session.query(UserOlBook).delete()
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
        print("👤 Users added.")


    # def add_books(self):
    #     self.book_list =
    #     for book in self.book_list:
    #         u_book = UserBook(
    #             owned=random.choice([True, False]),
    #             status=random.choice([status for status in BookStatus]),
    #             user=random.choice([self.user1, self.user2]),
    #             book=book
    #         )
    #         self.db.session.add(u_book)
    #     self.db.session.commit()
    #     print("📚 Books added.")