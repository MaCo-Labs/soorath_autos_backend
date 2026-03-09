# Backend/myapp/signals.py
import logging
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from .models import Vehicle, VehicleImage

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=VehicleImage)
def delete_vehicle_image_file(sender, instance, **kwargs):
    """Delete the gallery image file from S3 when the VehicleImage row is deleted."""
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception as e:
            logger.warning("Failed to delete VehicleImage file from S3: %s", e)


@receiver(pre_delete, sender=Vehicle)
def delete_vehicle_main_image_file(sender, instance, **kwargs):
    """Delete the main image file from S3 when the Vehicle is deleted.
    Gallery images are handled by the VehicleImage pre_delete signal
    (Django fires pre_delete on each cascaded child)."""
    if instance.image:
        try:
            instance.image.delete(save=False)
        except Exception as e:
            logger.warning("Failed to delete Vehicle main image from S3: %s", e)


@receiver(pre_save, sender=Vehicle)
def cleanup_old_main_image(sender, instance, **kwargs):
    """When the main image is replaced, delete the old file from S3."""
    if not instance.pk:
        return  # New object, nothing to clean up

    try:
        old = Vehicle.objects.get(pk=instance.pk)
    except Vehicle.DoesNotExist:
        return

    if old.image and old.image != instance.image:
        try:
            old.image.delete(save=False)
        except Exception as e:
            logger.warning("Failed to delete old Vehicle main image from S3: %s", e)
