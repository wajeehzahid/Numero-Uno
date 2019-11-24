from datetime import datetime
from typing import Tuple
from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint

from app import social_network


# class Users(social_network.Model):
#     user_id = social_network.Column(social_network.BIGINT, primary_key=True, nullable=False, autoincrement=True, )
#     name = social_network.Column(social_network.String(50), nullable=False)
#     email = social_network.Column(social_network.String(255), unique=True, nullable=False)
#     password = social_network.Column(social_network.String(255), nullable=False)
#     profile_picture_url = social_network.Column(social_network.String(255), nullable=False, default='')
#     Posts = social_network.relationship('posts', backref='author', lazy=True)
#
#     def __repr__(self):
#         return f"Users('{self.username}', '{self.email}', '{self.image_file}')"
#
#
# class Posts(social_network.Model):
#     post_id = social_network.Column(social_network.BIGINT, primary_key=True, nullable=False)
#     date_posted = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)
#     content = social_network.Column(social_network.Text, nullable=False)
#     user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                     nullable=False)
#
#     def __repr__(self):
#         return f"Posts('{self.title}', '{self.date_posted}')"
#
#
# class Likes(social_network.Model):
#     user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                     nullable=False)
#     post_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('posts.post_id'),
#                                     nullable=False)
#     __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'post_id', name='user_post'),)
#
#
# class Friends(social_network.Model):
#     user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                     nullable=False)
#     friend_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                       nullable=False)
#     __table_args__: Tuple[PrimaryKeyConstraint] = (PrimaryKeyConstraint('user_id', 'friend_id', name='user_friend'),)
#
#
# class Messages(social_network.Model):
#     message_id = social_network.Column(social_network.BIGINT, nullable=False, autoincrement=True, primary_key=True)
#     content = social_network.Column(social_network.Text, nullable=False)
#     date_created = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)
#     user_id_from = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                          nullable=False)
#     user_id_to = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                        nullable=False)
#
#
# class Comments(social_network.Model):
#     comment_id = social_network.Column(social_network.BIGINT, nullable=False, autoincrement=True, primary_key=True)
#     user_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('users.user_id'),
#                                     nullable=False)
#     post_id = social_network.Column(social_network.BIGINT, social_network.ForeignKey('posts.post_id'),
#                                     nullable=False)
#     content = social_network.Column(social_network.Text, nullable=False)
#     date_posted = social_network.Column(social_network.DateTime, nullable=False, default=datetime.utcnow)
