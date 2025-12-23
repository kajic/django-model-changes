from django.db import models

from django_model_changes.changes import ChangesMixin


class User(ChangesMixin):
    name = models.CharField(max_length=100)
    flag = models.BooleanField(default=False)


class Article(ChangesMixin):
    title = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
