'''Test user_views'''
# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, bcrypt, Likes
from bs4 import BeautifulSoup

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

class UserViewsTests(TestCase):
    '''Test case for user view functions'''
    def setUp(self):
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        self.client = app.test_client()
        self.testuser = User.signup(
            username="testuserlen",
            password="password",
            image_url=None,
            email="testemail@hotmail.com"
        )
        self.testuser_id = 10000
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)
        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_unloggedin_home(self):
        '''homepage if user is not logged in'''
        resp = self.client.get('/')
        html = resp.get_data(as_text=True)
        self.assertIn('Sign up now to get your own personalized timeline!', html)

    def test_loggedin_view(self):
        '''homepage if user is logged in'''
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Log out', html)

    def setup_likes(self):
        m1 = Message(text="trending warble", user_id=self.testuser_id)
        m2 = Message(text="Eating some lunch", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id=self.testuser_id, message_id=9876)

        db.session.add(l1)
        db.session.commit()
    
    def test_user_likes_number(self):
        self.setup_likes()

        with self.client as c:
            resp = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(resp.status_code, 200)

            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all('li', {'class': 'stat'})
            self.assertEqual(len(found), 4)

            # 2 count of messages
            self.assertIn('2', found[0].text)

            # 0 count of followers
            self.assertIn('0', found[1].text)

            # 0 count of folliwing
            self.assertIn('0', found[2].text)

            # 1 count of likes
            self.assertIn('1', found[3].text)