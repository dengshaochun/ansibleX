web: ~/.virtualenv/devOps/bin/python manage.py runserver 0.0.0.0:8000
worker: ~/.virtualenv/devOps/bin/celery -A devOps worker -l debug
beat: ~/.virtualenv/devOps/bin/celery -A devOps beat -l debug --scheduler django_celery_beat.schedulers:DatabaseScheduler
