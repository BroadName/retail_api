from django.contrib import admin
from .models import CustomUser, Contact, ConfirmToken


admin.site.register(CustomUser)
admin.site.register(Contact)
admin.site.register(ConfirmToken)