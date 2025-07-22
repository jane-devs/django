from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Like, Video


@receiver(post_save, sender=Like)
def increase_total_likes(sender, instance, created, **kwargs):
    if created:
        instance.video.total_likes = instance.video.likes.count()
        instance.video.save(update_fields=['total_likes'])


@receiver(post_delete, sender=Like)
def decrease_total_likes(sender, instance, **kwargs):
    if instance.video_id:
        video = Video.objects.filter(id=instance.video_id).first()
        if video:
            video.total_likes = video.likes.count()
            video.save(update_fields=['total_likes'])
