"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy.exc import IntegrityError as ie

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test for Message model."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            id=10000,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()
        # Creating message
        message = Message(id=100, text="Test text", user_id=10000)
        db.session.add(message)
        db.session.commit()

        self.client = app.test_client()
    
    def test_creating_message(self):
        """Testing creating Message"""
        new_message = Message(id=10, text="Second message", user_id=10000)
        db.session.add(new_message)
        db.session.commit()
        self.assertTrue(Message.query.get(10))
        self.assertEqual(Message.query.count(), 2)

    def test_message_create_fail(self):
        """Testing creating Message fail"""
        attempt_1 = Message(id=10, user_id=10000)
        with self.assertRaises(ie):
            db.session.add(attempt_1)
            db.session.commit()
            db.session.rollback()

    def test_message_model(self):
        """Testing Message model"""
        m = Message.query.get(100)
        self.assertEqual(len(m.liked_users), 0)
        self.assertEqual(m.user.id, 10000)
    