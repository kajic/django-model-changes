from django.db import models

from django_model_changes import ChangesMixin


class User(ChangesMixin, models.Model):
    name = models.CharField(max_length=100)
    flag = models.BooleanField(default=False)


class Article(ChangesMixin, models.Model):
    title = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
