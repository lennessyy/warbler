"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, bcrypt

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
        self.client = app.test_client()

        u1 = User(
            email="test123@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # m1 = Message(
        #     text="test message",
        #     user_id = 1   
        # )

        # m2 = Message(
        #     text="test message2",
        #     user_id = 2
        # )

        # db.session.add(m1)
        # db.session.add(m2)
        # db.session.commit()

    def tearDown(self):
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

        #different attributes should be as expected
        self.assertEqual(u.email, "test@test.com")
        self.assertEqual(u.username, "testuser")
        self.assertEqual(u.password, "HASHED_PASSWORD")

    def test_user_following(self):
        '''Does follow and unfollow work'''
        users = User.query.all()
        users[0].followers.append(users[1])
        self.assertIn(users[1], users[0].followers)

        users[0].followers.remove(users[1])
        self.assertNotIn(users[1], users[0].followers)
    

    def test_user_signup(self):
        '''Does the signup function work?'''
        user = User.signup(username="testuser123",
        password="password",
        email="testemail@email.com",
        image_url="image.jpg")

        new_user = User.query.filter(User.username=="testuser123").one()
        self.assertEqual(user, new_user)

    def test_user_authenticate(self):
        '''Does authenticate return user when password is correct and False when incorrect'''
        user = User.signup(username="testuser123",
        password="password",
        email="testemail@email.com",
        image_url="image.jpg")

        authenticated = User.authenticate(username="testuser123", password="password")
        self.assertEqual(authenticated, user)
        self.assertFalse(User.authenticate(username="testuser123", password="password2121212"))

    