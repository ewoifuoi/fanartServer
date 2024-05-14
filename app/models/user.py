from tortoise import fields
from tortoise.models import Model


class RegistrationRequest(Model): ### 用于记录用户邮箱验证前的请求
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=30)
    password = fields.CharField(max_length=100)
    name = fields.CharField(max_length=20)
    url = fields.CharField(max_length=50)
    timestamp = fields.DatetimeField(auto_now_add=True)
