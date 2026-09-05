from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Penduduk, Dusun, Lorong


@receiver(post_save, sender=Penduduk)
def update_dusun_lorong_population_on_penduduk_save(sender, instance, created, **kwargs):
    """Update population count when penduduk is saved"""
    if instance.dusun:
        instance.dusun.save()  # This will trigger auto-calculation
    
    if instance.lorong:
        instance.lorong.save()  # This will trigger auto-calculation


@receiver(post_delete, sender=Penduduk)
def update_dusun_lorong_population_on_penduduk_delete(sender, instance, **kwargs):
    """Update population count when penduduk is deleted"""
    if instance.dusun:
        instance.dusun.save()  # This will trigger auto-calculation
    
    if instance.lorong:
        instance.lorong.save()  # This will trigger auto-calculation

