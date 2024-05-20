from tortoise import fields
from tortoise.models import Model

class Service(Model):
    id = fields.IntField(pk=True)
    service_name = fields.CharField(max_length=30)
    function = fields.CharField(max_length=30)
    last_updated = fields.DatetimeField(auto_now=True)
    duration = fields.IntField(default=0)

class Cookie(Model):
    cookie = fields.CharField(max_length=1000)
