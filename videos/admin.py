from django.contrib import admin
from .models import Video, VideoFile


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'is_published', 'total_likes', 'created_at')
    search_fields = ('name', 'owner__username')
    list_filter = ('is_published', 'created_at')


@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'quality')
    list_filter = ('quality',)
