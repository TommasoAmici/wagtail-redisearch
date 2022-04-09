test:
	poetry run pytest --doctest-modules tests/ wagtail_redisearch/

test-all:
	tox --parallel
