from datetime import datetime
from typing import Tuple
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from app import db


# class Users(db.Model):
#     user_id = db.Column(db.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(255), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)
#     profile_picture_url = db.Column(db.String(255), nullable=False, default='')
#     Posts = db.relationship('posts', backref='author', lazy=True)
#
#     def __repr__(self):
#         return f"Users('{self.username}', '{self.email}', '{self.image_file}')"
#
#
# class Posts(db.Model):
#     post_id = db.Column(db.BIGINT, primary_key=True, nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                     nullable=False)
#
#     def __repr__(self):
#         return f"Posts('{self.title}', '{self.date_posted}')"
#
#
# class Likes(db.Model):
#     user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                     nullable=False)
#     post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'),
#                                     nullable=False)
#     __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)
#
#
# class Friends(db.Model):
#     user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                     nullable=False)
#     friend_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                       nullable=False)
#     __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)
#
#
# class Messages(db.Model):
#     message_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
#     content = db.Column(db.Text, nullable=False)
#     date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     user_id_from = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                          nullable=False)
#     user_id_to = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                        nullable=False)
#
#
# class Comments(db.Model):
#     comment_id = db.Column(db.BIGINT, nullable=False, autoincrement=True, primary_key=True)
#     user_id = db.Column(db.BIGINT, db.ForeignKey('users.user_id'),
#                                     nullable=False)
#     post_id = db.Column(db.BIGINT, db.ForeignKey('posts.post_id'),
#                                     nullable=False)
#     content = db.Column(db.Text, nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)




