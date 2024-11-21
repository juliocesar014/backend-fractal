poetry shell
poetry run python manage.py migrate
poetry run python manage.py runserver
poetry add --dev pytest pytest-django
poetry add --dev flake8
