from django.urls import path
from .views import (
    VideoDetailView,
    VideoListView,
    VideoIDListView,
    VideoLikeToggleView,
    VideoStatisticsSubqueryView,
    VideoStatisticsGroupByView
)

app_name = 'videos'

urlpatterns = [
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('', VideoListView.as_view(), name='video-list'),
    path('ids/', VideoIDListView.as_view(), name='video-ids'),
    path('<int:pk>/likes/', VideoLikeToggleView.as_view(), name='video-like-toggle'),
    path('statistics-subquery/', VideoStatisticsSubqueryView.as_view(), name='video-statistics-subquery'),
    path('statistics-group-by/', VideoStatisticsGroupByView.as_view(), name='video-statistics-group-by'),
]
