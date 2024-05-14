from tortoise import fields
from tortoise.models import Model


class RegistrationRequest(Model): ### 用于记录用户邮箱验证前的请求
    email = fields.CharField(pk=True, max_length=30)
    id = fields.CharField(max_length=100)
    password = fields.CharField(max_length=100)
    name = fields.CharField(max_length=20)
    timestamp = fields.DatetimeField(auto_now=True)
