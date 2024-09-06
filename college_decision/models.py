from django.db import models


class Payment(models.Model):
    user_email = models.EmailField()  # Store the email address from Stripe
    emails_purchased = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_email',)  # Ensure each email is unique

