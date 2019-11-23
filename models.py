from datetime import datetime
from typing import Tuple
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from app import socialnetworking


class Users(socialnetworking.Model):
    user_id = socialnetworking.Column(socialnetworking.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
    name = socialnetworking.Column(socialnetworking.String(50), nullable=False)
    email = socialnetworking.Column(socialnetworking.String(255), unique=True, nullable=False)
    password = socialnetworking.Column(socialnetworking.String(255), nullable=False)
    profile_picture_url = socialnetworking.Column(socialnetworking.String(255), nullable=False, default='')
    Posts = socialnetworking.relationship('posts', backref='author', lazy=True)

    def __repr__(self):
        return f"Users('{self.username}', '{self.email}', '{self.image_file}')"


class Posts(socialnetworking.Model):
    post_id = socialnetworking.Column(socialnetworking.BIGINT, primary_key=True, nullable=False)
    date_posted = socialnetworking.Column(socialnetworking.DateTime, nullable=False, default=datetime.utcnow)
    content = socialnetworking.Column(socialnetworking.Text, nullable=False)
    user_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                      nullable=False)

    def __repr__(self):
        return f"Posts('{self.title}', '{self.date_posted}')"


class Likes(socialnetworking.Model):
    user_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                      nullable=False)
    post_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('posts.post_id'),
                                      nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)

class Friends(socialnetworking.Model):
    user_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                      nullable=False)
    friend_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                        nullable=False)
    __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)

class Messages(socialnetworking.Model):
    message_id = socialnetworking.Column(socialnetworking.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    content = socialnetworking.Column(socialnetworking.Text, nullable=False)
    date_created = socialnetworking.Column(socialnetworking.DateTime, nullable=False, default=datetime.utcnow)
    user_id_from = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                           nullable=False)
    user_id_to = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                         nullable=False)

class Comments(socialnetworking.Model):
    comment_id = socialnetworking.Column(socialnetworking.BIGINT, nullable=False, autoincrement=True, primary_key=True)
    user_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('users.user_id'),
                                      nullable=False)
    post_id = socialnetworking.Column(socialnetworking.BIGINT, socialnetworking.ForeignKey('posts.post_id'),
                                      nullable=False)
    content = socialnetworking.Column(socialnetworking.Text, nullable=False)
    date_posted = socialnetworking.Column(socialnetworking.DateTime, nullable=False, default=datetime.utcnow)