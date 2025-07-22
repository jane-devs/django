from django.db.models import Subquery, OuterRef, Sum
from users.models import CustomUser
from videos.models import Video


def get_users_likes_sum_subquery():
    """Получаем сумму лайков юзера."""
    published_videos = Video.objects.filter(
        is_published=True,
        owner=OuterRef('pk')
    ).values('owner').annotate(
        total=Sum('total_likes')
    ).values('total')

    return CustomUser.objects.annotate(
        likes_sum=Subquery(published_videos)
    ).order_by('-likes_sum')
