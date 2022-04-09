from integration.home.models import BasePage
from wagtail.core.models import Page
from wagtail_redisearch.backend import (
    RediSearchBackend,
    RediSearchModelIndex,
    get_model_root,
)


def test_get_model_root():
    assert get_model_root(Page) == Page
    assert get_model_root(BasePage) == Page


def test_RediSearchModelIndex():
    backend = RediSearchBackend({})
    index = RediSearchModelIndex(backend, "wagtail_Page", Page)
    assert index.document_key(123) == "wagtail_Page:123"
