from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import FinancialProfile, Category


BASE_CATEGORIES = [
    "Alimentation",
    "Transport",
    "Divertissement",
    "Shopping",
    "Santé",
    "Abonnements",
    "Autres",
]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_and_categories(sender, instance, created, **kwargs):
    if not created:
        return

    # Profil financier auto
    FinancialProfile.objects.create(user=instance)

    # Catégories de base auto (propres à l'user)
    for name in BASE_CATEGORIES:
        Category.objects.get_or_create(user=instance, name=name)
