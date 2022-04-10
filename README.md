[![!PyPi version](https://img.shields.io/pypi/v/wagtail-redisearch.svg)](https://pypi.org/project/wagtail-redisearch/)
[![!Python versions](https://img.shields.io/pypi/pyversions/wagtail-redisearch.svg)](https://pypi.org/project/wagtail-redisearch/)
[![!CI/CD status](https://github.com/TommasoAmici/wagtail-redisearch/actions/workflows/build.yaml/badge.svg)](https://github.com/TommasoAmici/wagtail-redisearch/actions/workflows/build.yaml)
[![!Code coverage status](https://codecov.io/gh/TommasoAmici/wagtail-redisearch/branch/main/graph/badge.svg)](https://codecov.io/gh/TommasoAmici/wagtail-redisearch)
[![!Formatted with Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# wagtail-redisearch

A Django app to use [RediSearch](https://redis.com/modules/redis-search/) as a search
backend in Wagtail.

## Requirements

- Django >= 3.2
- Wagtail >= 2.15
- RediSearch v2

## Usage

Install [`wagtail-redisearch`](https://pypi.org/project/wagtail-redisearch/) from PyPi.

In your `settings.py` configure your search backend as follows:

```py
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail_redisearch",
        # optional parameters
        "INDEX": "custom-index-name", # default: "wagtail"
        "HOST": "127.0.0.1",
        "PORT": 6379,
        # you can add any option here to be used when initializing
        # a Redis client with redis-py.
        # e.g.
        "retry_on_error": True
    }
}
```

For more information about what options you can pass to the Redis client, look at the [official documentation](https://redis.readthedocs.io/en/stable/connections.html#generic-client).

`wagtail-redisearch` implements the interfaces described in [Backends Rolling your own](https://docs.wagtail.org/en/stable/topics/search/backends.html#rolling-your-own), thus usage in Wagtail requires no special adjustment.

To configure search on your models, follow the [official Wagtail documentation](https://docs.wagtail.org/en/stable/topics/search/index.html).

## Contributing

To contribute to this project you'll need RediSearch installed and `poetry`.

```sh
# install dependencies
poetry install

# run tests
make test

# run tests with tox
make test-all

# to run a minimal Wagtail application to test things out
make run
```
