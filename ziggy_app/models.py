
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils import timezone


class Ingredients(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


DIFFICULTY_LEVEL = ((1, "easy"),
                    (2, "almost easy"),
                    (3, "medium"),
                    (4, "almost expert"),
                    (5, "expert"))


class Recipe(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=100)
    preparation_time = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVEL)
    ingredients = models.ManyToManyField(Ingredients, through='Amounts')
    upload_date = models.DateTimeField(default=timezone.now())
    instructions = models.TextField(blank=True)
    #TODO maybe need also likes field that sums all the likes and gets updated when a like is given
    #TODO or maybe a many to many field of all user the like it

    def likes(self):
        return Likes.objects.filter(liked=self, like=True).count()


UNIT_TYPES = ((1, "cup"),
              (2, "table spoon"),
              (3, "tea spoon"),
              (4, "pinch"),
              (5, "gram"),
              (6, "milliliter"),
              (7, "unit"), )


class Amounts(models.Model):
    recipe = models.ForeignKey(Recipe)
    ingredient = models.ForeignKey(Ingredients)
    amount = models.IntegerField()
    unit = models.IntegerField(choices=UNIT_TYPES)

    def __str__(self):
        if self.unit == 7:
            return str(self.amount) + " " + str(self.ingredient) + "s"
        return str(self.amount) + " " + self.get_unit_display() + " of " + str(self.ingredient)


class Likes(models.Model):
    liker = models.ForeignKey(User)
    liked = models.ForeignKey(Recipe)
    like = models.BooleanField(default=False)

    class Meta:
        unique_together = ('liker', 'liked')

    def to_button(self):
        return "unlike" if self.like else "like"
