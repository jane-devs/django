from django.urls import path
from .views import (
    VideoDetailView,
    VideoListView,
    VideoIDListView,
    VideoLikeToggleView,
)

app_name = 'videos'

urlpatterns = [
    path('<int:pk>/', VideoDetailView.as_view(), name='video-detail'),
    path('', VideoListView.as_view(), name='video-list'),
    path('ids/', VideoIDListView.as_view(), name='video-ids'),
    path('<int:pk>/likes/', VideoLikeToggleView.as_view(), name='video-like-toggle'),
]
