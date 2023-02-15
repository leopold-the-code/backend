from tortoise import fields, models
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, null=True)
    name = fields.CharField(max_length=255, null=True)
    surname = fields.CharField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    birth_date = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=255, null=True)
    token = fields.CharField(max_length=255, null=True)


User_Pydantic = pydantic_model_creator(Users, name="User")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)
