from django.core.mail import EmailMessage
from django.conf import settings


def send_order_confirmation_email(user_email, invoice_path, order_uid):
    subject = "Order Confirmed – Saree Store"
    body = f"""
Hi,

Your order has been successfully placed!

Order ID: {order_uid}

Please find the invoice attached.

Thank you for shopping with us.
Saree Store Team
"""

    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [user_email]
    )

    email.attach_file(invoice_path)
    email.send()
