from django.db import models
from django.utils import timezone
from datetime import timedelta


class Payment(models.Model):
    user_email = models.EmailField()  # Store the email address from Stripe
    emails_purchased = models.IntegerField(default=0)
    emails_sent = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_email',)  # Ensure each email is unique


class UniversityDecision(models.Model):
    DECISION_TYPES = [
        ('Acceptance', 'Acceptance'),
        ('Rejection', 'Rejection'),
    ]

    university = models.CharField(max_length=100)
    decision_type = models.CharField(max_length=20, choices=DECISION_TYPES)
    decision_count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('university', 'decision_type')

    def __str__(self):
        return f"{self.university} - {self.decision_type} ({self.decision_count})"


class LetterGeneration(models.Model):
    email = models.EmailField(unique=True)  # Primary identifier
    full_name = models.CharField(max_length=255)
    first_generated_at = models.DateTimeField(auto_now_add=True)  # When first letter was generated
    last_generated_at = models.DateTimeField(auto_now=True)  # Updates on each generation
    letters_generated = models.IntegerField(default=1)  # Counter for total letters

    class Meta:
        verbose_name = "Letter Generation"
        verbose_name_plural = "Letter Generations"

    def __str__(self):
        return f"{self.email} ({self.letters_generated} letters)"

    @classmethod
    def get_total_letters_generated(cls):
        """Returns the total number of letters generated across all users"""
        return cls.objects.aggregate(total=models.Sum('letters_generated'))['total'] or 0


class DecisionToken(models.Model):
    token = models.CharField(max_length=64, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    university = models.CharField(max_length=100)
    decision = models.CharField(max_length=20)  # Acceptance/Rejection
    email = models.EmailField()
    application_id = models.CharField(max_length=20)  # For realism
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    viewed = models.BooleanField(default=False)
    viewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.email} - {self.university} ({self.decision})"

    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at

    def mark_viewed(self):
        """Mark the token as viewed"""
        self.viewed = True
        self.viewed_at = timezone.now()
        self.save(update_fields=['viewed', 'viewed_at'])

