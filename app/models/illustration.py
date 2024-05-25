from tortoise import Model
from tortoise.fields import IntField, CharField, TextField,DatetimeField, ForeignKeyField,ManyToManyField,OnDelete,TextField


class Illustration(Model):
    IllustrationID = CharField(max_length=100,pk=True)
    Title = CharField(max_length=20)
    Description = TextField(max_length=500, null=True)
    Location = CharField(max_length=100)
    Height = IntField()
    Width = IntField()
    FileSize = IntField()
    FileType = CharField(max_length=10)
    LikeCount = IntField(default=0)
    ViewCount = IntField(default=0)
    CreatedAt = DatetimeField(auto_now_add=True)
    UserID = ForeignKeyField('models.User',related_name='Illustrations')
    Tags = ManyToManyField('models.Tag',related_name='Illustrations',through='illustration.IllustrationTag')

    FavoritedBy = ManyToManyField('models.User', related_name='Favorites',through='illustration.Favorite')
    LikedBy = ManyToManyField('models.User', related_name='Likes', through='illustration.Like')

class Tag(Model):
    TagID = IntField(pk=True)
    TagName = CharField(max_length=20)
    CreatedAt = DatetimeField(auto_now_add=True)


class IllustrationTag(Model):
    IllustrationID = ForeignKeyField('models.Illustration',related_name='IllustrationTags')
    TagID = ForeignKeyField('models.Tag',related_name='IllustrationTags')

class Like(Model):
    UserID = ForeignKeyField('models.User', on_delete=OnDelete.CASCADE)
    IllustrationId = ForeignKeyField('models.Illustration', on_delete=OnDelete.CASCADE)
    CreatedAt = DatetimeField(auto_now=True)

class Favorite(Model):
    UserID = ForeignKeyField('models.User',  on_delete=OnDelete.CASCADE)
    IllustrationId = ForeignKeyField('models.Illustration',  on_delete=OnDelete.CASCADE)
    CreatedAt = DatetimeField(auto_now=True)

