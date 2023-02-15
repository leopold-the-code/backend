from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, null=True)
    name = fields.CharField(max_length=255, null=True)
    surname = fields.CharField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    birth_date = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=255, null=True)
    token = fields.CharField(max_length=255, null=True)
