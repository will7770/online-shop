from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review


@receiver(post_save, sender=Review)
def update_reviews_on_delete(sender, instance, **kwargs):
    instance.item.update_rating()

@receiver(post_delete, sender=Review)
def update_reviews_on_delete(sender, instance, **kwargs):
    instance.item.update_rating()