web: gunicorn -w 4 -b 0.0.0.0:5000 app.app:app
worker: celery -A app.tasks worker --loglevel=info
