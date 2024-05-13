from tortoise import fields
from tortoise.models import Model


class Image(Model):
    id = fields.CharField(pk=True, max_length=50)
    location = fields.CharField(max_length=100, unique=True)
    has_compressed = fields.BooleanField(default=False)
    url = fields.CharField(max_length=100, unique=True)
    title = fields.CharField(max_length=50)
    likeCount = fields.IntField(default=0)
    viewCount = fields.IntField(default=0)
    datetime = fields.DatetimeField(auto_now_add=True)
    height = fields.IntField()
    width = fields.IntField()
    source = fields.CharField(max_length=50)

    author = fields.ForeignKeyField("models.Author", related_name="image")
    tags = fields.ManyToManyField("models.Tag", related_name='images')

class Author(Model):
    uid = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    source = fields.CharField(max_length=50)
    lastUpdatedTime = fields.DatetimeField()


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)


class User_Info(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)

