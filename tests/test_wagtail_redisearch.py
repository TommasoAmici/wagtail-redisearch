from django.db.models.expressions import Col
from django.db.models.lookups import Exact
from integration.home.models import BasePage
from wagtail.core.models import Page
from wagtail_redisearch.backend import (
    RediSearchBackend,
    RediSearchModelIndex,
    build_filters,
    get_model_root,
)


def test_get_model_root():
    assert get_model_root(Page) == Page
    assert get_model_root(BasePage) == Page


def test_build_filters():
    assert (
        build_filters(Exact(Col("wagtailcore_page", Page.live.field), True))
        == "@live:{1}"
    )
    assert (
        build_filters(Exact(Col("wagtailcore_page", Page.live.field), False))
        == "@live:{0}"
    )


def test_RediSearchModelIndex():
    backend = RediSearchBackend({})
    index = RediSearchModelIndex(backend, "wagtail_Page", Page)
    assert index.document_key(123) == "wagtail_Page:123"
