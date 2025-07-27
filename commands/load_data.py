import os
import sys
import random
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'youtube.settings')
django.setup()

from django.db.models.signals import post_delete
from django.db import connection

from users.models import CustomUser
from videos.models import Video, Like
from videos.signals import decrease_total_likes

NUM_USERS = 10_000
NUM_VIDEOS = 100_000
BATCH_SIZE = 1000
MAX_LIKES_PER_VIDEO = 10
RESET_BEFORE_INSERT = False


def reset_database():
    if RESET_BEFORE_INSERT:
        print('Отключаем сигнал decrease_total_likes временно...')
        post_delete.disconnect(decrease_total_likes, sender=Like)
        print('Очищаем базу данных...')
        Like.objects.all().delete()
        print('Очистили лайки...')
        Video.objects.all().delete()
        print('Очистили видео...')
        CustomUser.objects.all().delete()
        print('Очистили юзеров...')
        print('База данных очищена.\n')
        print('Восстанавливаем сигнал decrease_total_likes...')
        post_delete.connect(decrease_total_likes, sender=Like)


def create_users():
    """Добавление юзеров в БД."""
    users = []
    for i in range(NUM_USERS):
        if i % 1000 == 0:
            print(f'Генерируем пользователя {i}/{NUM_USERS}')
        user = CustomUser(
            username=f'user_{i}',
            email=f'user_{i}@example.com',
            bio=f'bio for user {i}',
            password='random_password'
        )
        users.append(user)

    CustomUser.objects.bulk_create(users, batch_size=BATCH_SIZE)
    print(f'Создано пользователей: {NUM_USERS}\n')


def create_videos():
    """Добавление видео в БД."""
    users = list(CustomUser.objects.all())
    videos = []
    for i in range(NUM_VIDEOS):
        owner = random.choice(users)
        video = Video(
            owner=owner,
            name=f'Video {i}',
            is_published=random.choice([True, False]),
            total_likes=0
        )
        videos.append(video)

        if len(videos) % BATCH_SIZE == 0:
            Video.objects.bulk_create(videos, batch_size=BATCH_SIZE)
            print(f'Добавлено видео: {len(videos)}')
            videos = []

    if videos:
        Video.objects.bulk_create(videos, batch_size=BATCH_SIZE)
    print(f'Всего создано видео: {NUM_VIDEOS}\n')


def create_likes():
    """Добавление лайков в БД."""
    users = list(CustomUser.objects.all())
    videos = list(Video.objects.all())
    likes = []
    count = 0

    for video in videos:
        number_of_likes = random.randint(0, MAX_LIKES_PER_VIDEO)
        liked_users = random.sample(users, k=number_of_likes)

        for user in liked_users:
            likes.append(Like(video=video, user=user))

        if len(likes) >= BATCH_SIZE:
            Like.objects.bulk_create(likes, batch_size=BATCH_SIZE, ignore_conflicts=True)
            count += len(likes)
            print(f'Добавлено лайков: {count}')
            likes = []

    if likes:
        Like.objects.bulk_create(likes, batch_size=BATCH_SIZE, ignore_conflicts=True)
        count += len(likes)

    print(f'Всего лайков: {count}\n')


def update_total_likes_sql():
    """Чистый SQL для ускорения процесса наполнения БД."""
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE videos_video AS v
            SET total_likes = sub.likes_count
            FROM (
                SELECT video_id, COUNT(*) AS likes_count
                FROM videos_like
                GROUP BY video_id
            ) AS sub
            WHERE v.id = sub.video_id
        """)
    print('Обновили total_likes через raw SQL')


if __name__ == '__main__':
    reset_database()
    print('Создаем пользователей...')
    create_users()
    print('Создаем видео...')
    create_videos()
    print('Создаем лайки...')
    create_likes()
    print('Обновляем total_likes...')
    update_total_likes_sql()
    print('Данные успешно загружены.')
