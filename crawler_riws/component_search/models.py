from django.db import models

# Create your models here.
class Click(models.Model):
    clicks = models.IntegerField(default=0, null=False)
    component = models.CharField(null=False, max_length=256)