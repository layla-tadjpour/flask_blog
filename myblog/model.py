from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from myblog import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create_user(cls, username, password):
        user = cls(username=username)
        user.set_password(password)
        db.session.add(user)
        #db.session.commit()
        return user

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first()

    @classmethod
    def authenticate_user(cls, username, password):
        user = cls.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.relationship('User', backref=db.backref('posts', lazy=True))

    @classmethod
    def create_post(cls, author_id, title, body):
        post = cls(author_id=author_id, title=title, body=body)
        db.session.add(post)
        return post

    @classmethod
    def get_post(cls, post_id):
        return cls.query.get(post_id)

    @classmethod
    def get_all_posts(cls):
        return cls.query.order_by(cls.created.desc()).all()

    @classmethod
    def update_post(cls, post_id, title, body):
        post = cls.get_post(post_id)
        if post:
            post.title = title
            post.body = body
            post.last_modified = datetime.utcnow()
            db.session.add(post)
        return post

    @classmethod
    def delete_post(cls, post_id):
        post = cls.get_post(post_id)
        if post:
            db.session.delete(post)
        return post
