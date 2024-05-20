
from tortoise import Model
from tortoise.fields import IntField, CharField, TextField,DatetimeField, ForeignKeyField,ManyToManyField,OnDelete

class Comment(Model):
    CommentID = CharField(max_length=100,pk=True)
    LikeCount = IntField(default=0)
    Content = TextField()
    CreatedAt = DatetimeField(auto_now=True)

    UserID = ForeignKeyField('models.User',related_name='Comments', on_delete=OnDelete.CASCADE)
    IllustrationID = ForeignKeyField('models.Illustration',related_name='Comments', on_delete=OnDelete.CASCADE)
    ParentCommentID = ForeignKeyField('models.Comment',related_name='ChildComments', on_delete=OnDelete.CASCADE)

class CommentLike(Model):
    UserID = ForeignKeyField('models.User',on_delete=OnDelete.CASCADE)
    CommentID = ForeignKeyField('models.Comment',on_delete=OnDelete.CASCADE)
    CreatedAt = DatetimeField(auto_now=True)
