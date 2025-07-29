from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    VideoViewSet,
    VideoIDListView,
    VideoLikeToggleView,
    VideoStatisticsSubqueryView,
    VideoStatisticsGroupByView
)


app_name = 'videos'
router = DefaultRouter()
router.register(r'', VideoViewSet, basename='video')

urlpatterns = [
    path('ids/', VideoIDListView.as_view(), name='video-ids'),
    path('<int:pk>/likes/', VideoLikeToggleView.as_view(), name='video-like-toggle'),
    path('statistics-subquery/', VideoStatisticsSubqueryView.as_view(), name='video-statistics-subquery'),
    path('statistics-group-by/', VideoStatisticsGroupByView.as_view(), name='video-statistics-group-by'),
    path('', include(router.urls)),
]
