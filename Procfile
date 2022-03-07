release: sh -c 'cd ./Spardha/ && python manage.py migrate'
web: gunicorn --pythonpath Spardha Spardha.wsgi
