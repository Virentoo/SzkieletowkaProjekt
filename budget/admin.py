from django.contrib import admin

from .models import User,Category,Income,Expense
# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Income)
admin.site.register(Expense)