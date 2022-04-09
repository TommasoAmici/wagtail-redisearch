from wagtail.core.models import Page
from wagtail_redisearch.backend import RediSearchBackend, RediSearchModelIndex


def test_RediSearchModelIndex():
    backend = RediSearchBackend({})
    index = RediSearchModelIndex(backend, "wagtail_Page", Page)
    assert index.document_key(123) == "wagtail_Page:123"
