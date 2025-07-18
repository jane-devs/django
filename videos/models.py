from django.db import models
from django.conf import settings


class Video(models.Model):
    """Сущность видеоролика."""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='videos'
    )
    is_published = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    total_likes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VideoFile(models.Model):
    """Сущность видеофайла."""
    class Quality(models.TextChoices):
        HD = 'HD', '720p'
        FHD = 'FHD', '1080p'
        UHD = 'UHD', '4K'
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to='videos/')
    quality = models.CharField(
        max_length=3,
        choices=Quality.choices
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['video', 'quality'],
                name='unique_video_quality'
            )
        ]

    def __str__(self):
        return f'{self.video.name} - {self.quality}'


class Like(models.Model):
    """Сущность Лайк."""
    video = models.ForeignKey(
        Video,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('video', 'user')

    def __str__(self):
        return f'{self.user} likes {self.video}'
