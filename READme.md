## Запуск приложения

1. Клонируй репозиторий и перейди в директорию:
```
git clone git@github.com:jane-devs/django.git
cd django
```

2. Создай .env файл по образу .env.example.

3. В терминале запусти docker-compose в daemon-режиме:
```
docker-compose build && docker-compose up -d
```

4. Проект доступен по адресу `localhost:8080`

