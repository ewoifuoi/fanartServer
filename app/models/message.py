from tortoise import fields
from tortoise.fields import IntField, TextField, ForeignKeyField, DateField, DatetimeField
from tortoise.models import Model

from models.user import User


class Message(Model):
    id = IntField(pk=True)
    content = TextField()
    from_user = ForeignKeyField('models.User', related_name='messageA')
    to_user = ForeignKeyField('models.User', related_name='messageB')
    CreatAt = DatetimeField(auto_now=True)

class MessageList(Model):
    id = IntField(pk=True)
    owner = ForeignKeyField('models.User', related_name='list')
    to_user = ForeignKeyField('models.User', related_name='messageC')
    CreatAt = DatetimeField(auto_now=True)
