from django.core.mail import send_mail

def send_otp_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your OTP is {otp}. Do not share it with anyone."
    send_mail(subject, message, "no-reply@sareestore.com", [email])
