
from tortoise.fields import IntField, TextField, DatetimeField, ForeignKeyField
from tortoise.models import Model

class Notice(Model):
    id = IntField(pk=True)
    type = IntField(default=0)
    content = TextField()
    IsReaded = IntField(default=0)
    UserID = ForeignKeyField("models.User", related_name="notice")
    CreatedAt = DatetimeField(auto_now=True)