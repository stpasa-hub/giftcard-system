from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Card)
def create_bonus_account(sender, instance, created, **kwargs):
    if created:
        BonusAccount.objects.create(card=instance)

