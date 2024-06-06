from tortoise import fields
from tortoise.fields import IntField, TextField, ForeignKeyField, DateField
from tortoise.models import Model

from models.user import User


class Message(Model):
    id = IntField(pk=True)
    content = TextField()
    from_user = ForeignKeyField('models.User', related_name='messageA')
    to_user = ForeignKeyField('models.User', related_name='messageB')
    CreatAt = DateField(auto_now_add=True)

class MessageList(Model):
    id = IntField(pk=True)
    owner = ForeignKeyField('models.User', related_name='list')
    to_user = ForeignKeyField('models.User', related_name='messageC')
    CreatAt = DateField(auto_now_add=True)
