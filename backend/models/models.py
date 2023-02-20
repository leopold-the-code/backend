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


class Image(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User")
    path = fields.CharField(max_length=500)


class Swipe(models.Model):
    id = fields.IntField(pk=True)
    swiper = fields.ForeignKeyField("models.User", "my_swipes")
    subject = fields.ForeignKeyField("models.User", "subject_in_swipes")
    side = fields.BooleanField()  # False is left, right otherwise
