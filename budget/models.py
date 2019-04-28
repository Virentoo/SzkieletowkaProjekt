from django.db import models


class User(models.Model):
    email = models.EmailField(max_length=50)
    login = models.CharField(max_length=20)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.login


class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="")
    monthly = models.BooleanField(default=False)

    def __str__(self):
        return "%s - %s" % (self.user, self.name)


class Income(models.Model):
    income_name = models.CharField(max_length=100)
    income_desc = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    income_date = models.DateTimeField('Income added')
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.income_name


class Expense(models.Model):
    expense_name = models.CharField(max_length=100)
    expense_desc = models.CharField(max_length=300)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    expense_date = models.DateTimeField('Expense added')
    amount = models.FloatField(default=0)

    def __str__(self):
        return self.expense_name
