from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="")
    monthly = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.user, self.name)


class Transaction(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=300)
    type = models.CharField(max_length=50, choices=(("income", "Income"), ("expense", "Expense")))
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    date = models.DateTimeField('Added')
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.name