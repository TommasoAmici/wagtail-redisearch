from datetime import datetime, timezone

from django.db.models import Q
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
    queryset = Page.objects.live()
    f = build_filters(queryset.query.where)
    assert f == "@live:{1}"

    queryset = Page.objects.exclude(live=True)
    f = build_filters(queryset.query.where)
    assert f == "-@live:{1}"

    queryset = Page.objects.filter(live=False)
    f = build_filters(queryset.query.where)
    assert f == "@live:{0}"

    queryset = Page.objects.filter(id=123)
    f = build_filters(queryset.query.where)
    assert f == "@wagtail_id:[123 123]"

    queryset = Page.objects.filter(id__gt=123)
    f = build_filters(queryset.query.where)
    assert f == "@wagtail_id:[(123 inf]"

    queryset = Page.objects.filter(id__gte=123)
    f = build_filters(queryset.query.where)
    assert f == "@wagtail_id:[123 inf]"

    queryset = Page.objects.filter(id__lt=123)
    f = build_filters(queryset.query.where)
    assert f == "@wagtail_id:[-inf (123]"

    queryset = Page.objects.filter(id__lte=123)
    f = build_filters(queryset.query.where)
    assert f == "@wagtail_id:[-inf 123]"

    queryset = Page.objects.exclude(id__lte=123)
    f = build_filters(queryset.query.where)
    assert f == "-@wagtail_id:[-inf 123]"

    queryset = Page.objects.live().exclude(id=123)
    f = build_filters(queryset.query.where)
    assert f == "@live:{1} -@wagtail_id:[123 123]"

    queryset = Page.objects.filter(Q(id=123) | Q(id=456))
    f = build_filters(queryset.query.where)
    assert f == "(@wagtail_id:[123 123]|@wagtail_id:[456 456])"

    queryset = (
        Page.objects.live()
        .filter(
            search_description="foo",
            first_published_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        )
        .exclude(id=123)
    )
    f = build_filters(queryset.query.where)
    assert (
        f
        == "@live:{1} @first_published_at:[1577836800.0 1577836800.0] @search_description:{foo} -@wagtail_id:[123 123]"
    )


def test_RediSearchModelIndex():
    backend = RediSearchBackend({})
    index = RediSearchModelIndex(backend, "wagtail_Page", Page)
    assert index.document_key(123) == "wagtail_Page:123"
