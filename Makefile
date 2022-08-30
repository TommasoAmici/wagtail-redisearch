test:
	poetry run pytest

test-all:
	tox --parallel

# Integration tests/example
PYM=poetry run python manage.py

run:
	${PYM} runserver

cleandb:
	rm db.sqlite3

initdb: cleandb migrate loaddata

migrate:
	${PYM} makemigrations
	${PYM} migrate

update-index:
	${PYM} update_index

FIXTURES = integration/home/fixtures/pages.json
dumpdata:
	${PYM} dumpdata > ${FIXTURES}

loaddata:
	${PYM} loaddata ${FIXTURES}

shell:
	${PYM} shell_plus

admin-user:
	${PYM} shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin', first_name='Admin', last_name='Admin')"
