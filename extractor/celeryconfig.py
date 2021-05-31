broker_url = 'amqp://guest:guest@localhost:15672'
result_backend = 'db+postgresql+psycopg2://guest:guest@localhost/extractor'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Madrid'
enable_utc = True