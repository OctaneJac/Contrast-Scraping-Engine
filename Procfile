celery: parallel --ungroup --halt now,fail=1 ::: 'celery -A celery_config worker --loglevel=info --concurrency=2 -E' 'celery -A celery_config beat --loglevel=info'
flower: celery -A celery_config flower --persistent=True --db=postgresql://contrast_database_owner:npg_sV9BHIXJ6YNj@ep-steep-star-a1533wrh-pooler.ap-southeast-1.aws.neon.tech/contrast_database?sslmode=require --port=5555