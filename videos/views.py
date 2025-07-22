from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.db import transaction

from .models import Video, Like
from .serializers import (
    VideoSerializer, VideoIDSerializer,
    VideoStatisticsSerializer
)
from .permissions import IsStaffOrOwnerOrPublished
from users.models import CustomUser
from users.services import get_users_likes_sum_subquery


class VideoDetailView(generics.RetrieveAPIView):
    """Получить видео по ID."""
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = [IsStaffOrOwnerOrPublished]


class VideoListView(generics.ListAPIView):
    """Список видео с пагинацией."""
    serializer_class = VideoSerializer
    permission_classes = [IsStaffOrOwnerOrPublished]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Video.objects.all()
        if user.is_authenticated:
            return Video.objects.filter(
                Q(is_published=True) | Q(owner=user)
            )
        return Video.objects.filter(is_published=True)


class VideoIDListView(generics.ListAPIView):
    """Получение списка опубликованных ID видео."""
    queryset = Video.objects.filter(is_published=True)
    serializer_class = VideoIDSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


class VideoLikeToggleView(APIView):
    """Взаимодействие с лайками."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        """Добавить лайк."""
        try:
            video = Video.objects.get(pk=pk, is_published=True)
        except Video.DoesNotExist:
            return Response(
                {'detail': 'Видео не найдено или не опубликовано.'},
                status=status.HTTP_404_NOT_FOUND
            )
        with transaction.atomic():
            _, created = Like.objects.get_or_create(user=request.user, video=video)
            if created:
                video.total_likes = video.likes.count()
                video.save()
        return Response(
            {'detail': 'Лайк поставлен.'},
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, pk):
        """Удалить лайк."""
        try:
            video = Video.objects.get(pk=pk, is_published=True)
        except Video.DoesNotExist:
            return Response(
                {'detail': 'Видео не найдено или не опубликовано.'},
                status=status.HTTP_404_NOT_FOUND
            )
        with transaction.atomic():
            deleted, _ = Like.objects.filter(user=request.user, video=video).delete()
            if deleted:
                video.total_likes = video.likes.count()
                video.save()
        return Response(
            {'detail': 'Лайк удалён.'},
            status=status.HTTP_204_NO_CONTENT
        )


class VideoStatisticsSubqueryView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = VideoStatisticsSerializer

    def get_queryset(self):
        return get_users_likes_sum_subquery()


class VideoStatisticsGroupByView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = VideoStatisticsSerializer

    def get_queryset(self):
        return CustomUser.objects.annotate(
            likes_sum=Coalesce(
                Sum('videos__total_likes', filter=Q(videos__is_published=True)),
                Value(0)
            )
        ).order_by('-likes_sum')
