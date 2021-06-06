broker_url = 'amqp://guest:guest@localhost'
#result_backend = 'db+postgresql+psycopg2://igor:GUCITusr@localhost/extractor'
result_backend = 'django-db'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Madrid'
enable_utc = True
