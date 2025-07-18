from rest_framework import serializers
from .models import Video, VideoFile, Like
from users.models import CustomUser


class VideoFileSerializer(serializers.ModelSerializer):
    """Сериализатор для видеофайла."""
    class Meta:
        model = VideoFile
        fields = ('id', 'file', 'quality')


class VideoSerializer(serializers.ModelSerializer):
    """Сериализатор для видеоролика."""
    owner = serializers.CharField(source='owner.username', read_only=True)
    files = VideoFileSerializer(many=True, read_only=True)

    class Meta:
        model = Video
        fields = (
            'id',
            'owner',
            'is_published',
            'name',
            'total_likes',
            'created_at',
            'files'
        )


class VideoIDSerializer(serializers.ModelSerializer):
    """Сериализатор для списка видео по ID."""
    class Meta:
        model = Video
        fields = ('id',)


class VideoStatisticsSerializer(serializers.Serializer):
    """Сериализатор статистики по лайкам."""
    username = serializers.CharField()
    likes_sum = serializers.IntegerField()
