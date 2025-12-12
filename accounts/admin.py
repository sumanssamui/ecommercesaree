from django.contrib import admin
from .models import User, EmailOTP, UserToken

admin.site.register(User)
admin.site.register(EmailOTP)
admin.site.register(UserToken)
