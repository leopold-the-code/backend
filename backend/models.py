from tortoise import fields, models
from backend.config import settings


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, null=True)
    name = fields.CharField(max_length=255, null=True)
    description = fields.CharField(max_length=255, null=True)
    birth_date = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=255, null=True)
    token = fields.CharField(max_length=255, null=True)

    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)

    tag_objects: fields.ManyToManyRelation["Tag"]
    image_objects: fields.ForeignKeyRelation["Image"]

    @property
    def tags(self) -> list[str]:
        return [tag.value for tag in self.tag_objects]

    @property
    def images(self) -> list[str]:
        return [
            f"{settings.site_url}/get_image/{image.id}" for image in self.image_objects
        ]


class Tag(models.Model):
    id = fields.IntField(pk=True)
    value = fields.CharField(max_length=255)
    user: fields.ManyToManyRelation["User"] = fields.ManyToManyField(
        "models.User", related_name="tag_objects"
    )

    def __repr__(self) -> str:
        return f"<Tag value {self.value}>"


class Image(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", "image_objects"
    )
    rawbytes = fields.BinaryField()


class Swipe(models.Model):
    id = fields.IntField(pk=True)
    swiper: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", "my_swipes"
    )
    subject: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", "subject_in_swipes"
    )
    side = fields.BooleanField()  # False is left, right otherwise


class Match(models.Model):
    id = fields.IntField(pk=True)
    # The person who swiped right first
    initializer: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", "my_inits"
    )
    # the person who also answered with a swipe to the right
    responder: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", "my_responds"
    )
