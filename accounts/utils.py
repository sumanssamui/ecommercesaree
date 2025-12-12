import random
from .models import EmailOTP

def create_otp(user):
    otp = str(random.randint(100000, 999999))

    EmailOTP.objects.create(
        user=user,
        otp=otp
    )

    return otp
