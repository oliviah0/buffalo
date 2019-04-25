"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py

import os
from unittest import TestCase

from models import db, User, Message, Follows

from sqlalchemy.exc import IntegrityError as ie, InvalidRequestError

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

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


        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.get(10000)

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        
        u = User.query.get(10000)

        db.session.add(u)
        db.session.commit()

        test_user = User.query.get(10000)
        
        self.assertEqual(str(u), f"<User #{test_user.id}: {test_user.username}, {test_user.email}>")

    def test_user1_following(self):
        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user_2 = User.query.get(10000)

        db.session.add(user_1)
        user_1.following.append(user_2)

        db.session.commit()
        # Test if user_2 is following user_1
        self.assertIn(user_2, user_1.following)
        user_1.following.pop()
        db.session.commit()
        # Detect user2 is no longer following user_1
        self.assertNotIn(user_2, user_1.following)

    def test_user1_followed_by(self):
        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user_2 = User.query.get(10000)

        db.session.add(user_1)
        user_2.followers.append(user_1)

        db.session.commit()
        # Test if user_1 is in user_2 followers
        self.assertIn(user_1, user_2.followers)
        user_2.followers.pop()
        db.session.commit()
        # Detect user_1 is no longer in user_2 followers
        self.assertNotIn(user_1, user_2.followers)

    def test_user_create(self):
        User.signup(username="user_9", email="user_9@email.com", password="user_9", image_url="/static/images/default-pic.png")
        db.session.commit()

        user = User.query.filter_by(username="user_9")
        self.assertTrue(user)
    
    def test_user_create_fail(self):
        User.signup(username="user_9", email="test@test.com", password="user_9", image_url="/static/images/default-pic.png")
        with self.assertRaises(ie):
            db.session.commit()
            db.session.rollback()
        # self.assertRaises(IntegrityError)

    def test_user_authenticate(self):
        """Test is successfull return a user when given a valid usernam and password"""
        u = User.signup(username="user_9", email="user_9@email.com", password="user_9", image_url="/static/images/default-pic.png")
        db.session.commit()
        result = u.authenticate("user_9", "user_9")
        self.assertTrue(result)
    
    def test_user_autheticate_fail_username(self):
        """ fail to return a user when the username is invalid?"""
        u = User.query.get(10000)
        result = u.authenticate("wrong_username", "HASHED_PASSWORD")
        self.assertFalse(result)
    
    def test_user_authenticate_fail_password(self):
        """fail to return a user when the password is invalid?"""
        u = User.query.get(10000)
     
        with self.assertRaises(ValueError):
            u.authenticate("testuser", "password")