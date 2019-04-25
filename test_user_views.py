"""User views tests."""

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

from app import app, CURR_USER_KEY

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
        self.u = u

        self.client = app.test_client()

        db.session.add(u)
        db.session.commit()

    def test_user_view_profile_info(self):
        """Testing if user view is rendering user information"""

        response = self.client.get('/users/10000')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'@testuser', response.data)
    
    def test_user_view_users_search(self):
        """Testing search results of users"""
        
        response = self.client.get('/users?q=testuser')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'@testuser', response.data)
    
    def test_user_view_following(self):
        """Testing the user following view"""
        
        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user_2 = User.query.get(10000)

        db.session.add(user_1)
        user_2.following.append(user_1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            response = self.client.get('/users/10000/following')

            self.assertEqual(response.status_code, 200)
            self.assertIn(b'@testuser2', response.data)
    
    def test_user_view_followers(self):
        """Testing the user followers view"""
        
        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user_2 = User.query.get(10000)

        db.session.add(user_1)
        user_2.following.append(user_1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            response = self.client.get('/users/10002/followers')
            
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'@testuser', response.data)
    
    def test_user_view_start_following(self):
        """Testing the user starts following"""
        
        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user_1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            response = self.client.post('/users/follow/10002', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            
            current_user_followers = User.query.get(10000).following
            following_user = User.query.get(10002)
            self.assertIn(following_user, current_user_followers)

    def test_user_view_stops_following(self):
        """Testing the user stops following"""

        user_1 = User(
            id=10002,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        user_2 = User.query.get(10000)

        db.session.add(user_1)
        user_2.following.append(user_1)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u.id

            response = self.client.post('/users/stop-following/10002', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Follows.query.count(), 0)
