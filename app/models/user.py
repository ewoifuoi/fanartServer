from tortoise import fields
from tortoise.fields import OnDelete
from tortoise.models import Model


class RegistrationRequest(Model): ### 用于记录用户邮箱验证前的请求
    email = fields.CharField(pk=True, max_length=30)
    id = fields.CharField(max_length=100)
    password = fields.CharField(max_length=100)
    name = fields.CharField(max_length=20)
    timestamp = fields.DatetimeField(auto_now=True)

class User(Model):
    UserID = fields.CharField(pk=True, max_length=100)
    Password = fields.CharField(max_length=100)
    Name = fields.CharField(max_length=20)
    Avatar = fields.CharField(max_length=200)
    RegisteredAt = fields.DatetimeField(auto_now=True)
    LastLogin = fields.DatetimeField(auto_now=True)
    OnlineStatus = fields.BooleanField(default=False)
    Email = fields.CharField(max_length=30)

class Relationship(Model):
    RelationshipID = fields.IntField(pk=True)
    UserID = fields.CharField(max_length=100)
    FollowedUserID = fields.CharField(max_length=100)
    CreatedAt = fields.DatetimeField(auto_now=True)

