from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.db.models import Q, Sum, Value
from django.db.models.functions import Coalesce
from django.db import transaction
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Video, Like
from .serializers import (
    VideoSerializer, VideoIDSerializer,
    VideoStatisticsSerializer
)
from .permissions import IsStaffOrOwnerOrPublished
from users.models import CustomUser
from users.services import get_users_likes_sum_subquery


class VideoViewSet(ReadOnlyModelViewSet):
    """Позволяет получить список видеороликов и детали конкретного видео.

    - Неавторизованные пользователи видят только опубликованные видео.
    - Авторизованные — опубликованные и свои.
    - Админы — все видео.
    """
    serializer_class = VideoSerializer
    permission_classes = [IsStaffOrOwnerOrPublished]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Video.objects.all()
        elif user.is_authenticated:
            return Video.objects.filter(Q(is_published=True) | Q(owner=user))
        return Video.objects.filter(is_published=True)


class VideoIDListView(generics.ListAPIView):
    """
    APIView для получения списка ID всех опубликованных видеороликов.

    Доступно только служебным пользователям. Возвращает плоский список без пагинации.
    """
    queryset = Video.objects.filter(is_published=True)
    serializer_class = VideoIDSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None


class VideoLikeToggleView(APIView):
    """
    APIView для добавления и удаления лайков к опубликованным видео.

    Доступно только авторизованным пользователям. Обеспечивает уникальность лайка
    и защищено транзакцией от гонок.
    """
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
    """
    APIView для получения статистики по лайкам пользователей (через подзапрос).

    Доступно только служебным пользователям. Возвращает количество лайков,
    суммированных по опубликованным видео каждого пользователя.
    """
    permission_classes = [IsAdminUser]
    serializer_class = VideoStatisticsSerializer

    def get_queryset(self):
        return get_users_likes_sum_subquery()


class VideoStatisticsGroupByView(generics.ListAPIView):
    """
    APIView для получения статистики по лайкам пользователей (через group by).

    Доступно только служебным пользователям. Использует группировку и агрегацию
    по опубликованным видео.
    """
    permission_classes = [IsAdminUser]
    serializer_class = VideoStatisticsSerializer

    def get_queryset(self):
        return CustomUser.objects.annotate(
            likes_sum=Coalesce(
                Sum('videos__total_likes', filter=Q(videos__is_published=True)),
                Value(0)
            )
        ).order_by('-likes_sum')
