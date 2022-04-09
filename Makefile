test:
	poetry run pytest

test-all:
	tox --parallel

# Integration tests/example
PYM=poetry run python manage.py

run:
	${PYM} runserver

migrate:
	${PYM} makemigrations
	${PYM} migrate

update-index:
	${PYM} update_index

shell:
	${PYM} shell

admin-user:
	${PYM} shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin', first_name='Admin', last_name='Admin')"
