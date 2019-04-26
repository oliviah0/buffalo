"""SQLAlchemy models for Warbler."""

from datetime import datetime

from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class LikedMessage(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'liked_messages'

    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete="cascade"),
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )


class Follows(db.Model):
    """Connection of a follower <-> followee."""

    __tablename__ = 'follows'

    user_being_followed_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,
    )

class DirectMessage(db.Model):
    """Model for Direct Message"""
    __tablename__ = "direct_messages"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_from_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    user_to_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade")
    )

    # direct_messages = db.relationship("User", foreign_keys=[user_from_id, user_to_id])



class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'
#   db.relationship("", backref=liked_user , cascase="all,delete")
    liked_messages = db.relationship("Message", backref="liked_users", secondary="liked_messages")

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    image_url = db.Column(
        db.Text,
        default="/static/images/default-pic.png",
    )

    header_image_url = db.Column(
        db.Text,
        default="/static/images/warbler-hero.jpg"
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    private = db.Column(
        db.Boolean,
        default=False,
        nullable=True
    )

    messages = db.relationship('Message')

    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    user_from = db.relationship(
            "User",
            secondary="direct_messages",
            primaryjoin=(DirectMessage.user_from_id == id),
            secondaryjoin=(DirectMessage.user_to_id == id)
    )

    user_to = db.relationship(
            "User",
            secondary="direct_messages",
            primaryjoin=(DirectMessage.user_to_id == id),
            secondaryjoin=(DirectMessage.user_from_id == id)
    )

  

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    def is_following(self, other_user):
        """Is this user following `other_use`?"""

        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    @classmethod
    def signup(cls, username, email, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False
    
    def show_messages(self):
        """Show messages"""
        messages = (Message
                    .query
                    .filter(Message.user_id == self.id)
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())
        return messages
    
    def show_private_account_messages(self, logged_in_user):
        """Show private account messages"""
        if self in logged_in_user.following:
            return self.show_messages()
        else:
            return []

class Message(db.Model):
    """An individual message ("warble")."""

    __tablename__ = 'messages'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    text = db.Column(
        db.String(140),
        nullable=False,
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow(),
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    user = db.relationship('User')






def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)