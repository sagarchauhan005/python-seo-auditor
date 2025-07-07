from django.db import models

# Create your models here.

class TagsCounter(models.Model):
    id = models.AutoField(primary_key=True)
    h1 = models.IntegerField(default=0)
    h2 = models.IntegerField(default=0)
    title = models.IntegerField(default=0)
    meta_title = models.IntegerField(default=0)
    meta_description = models.IntegerField(default=0)
    og_title = models.IntegerField(default=0)
    og_description = models.IntegerField(default=0)

class Website(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120)
    url = models.URLField(default="")