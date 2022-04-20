from datetime import datetime, timezone

from django.core.management import call_command
from django.db.models import Q
from django.test import TestCase

from wagtail.core.models import Page
from wagtail.search.index import SearchField

from redis.commands.search.field import NumericField, TagField, TextField

from integration.home.models import BasePage
from wagtail_redisearch.backend import (
    RediSearchBackend,
    RediSearchModelIndex,
    build_filter_fields,
    build_filters,
    get_model_root,
    get_redis_field,
)


def test_get_model_root():
    assert get_model_root(Page) == Page
    assert get_model_root(BasePage) == Page


def test_build_filter_fields():
    qs = BasePage.objects.all()

    f = build_filter_fields(qs, ["title", "body"])
    assert f == "title|body"

    f = build_filter_fields(qs, ["author"])
    assert f == "author__name|author__date_of_birth"

    f = build_filter_fields(qs, ["title", "author"])
    assert f == "title|author__name|author__date_of_birth"


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


def test_get_redis_field():
    have = get_redis_field(BasePage, SearchField("test_text_field", boost=3))
    want = TextField("test_text_field", weight=3)
    assert have.args == want.args

    have = get_redis_field(BasePage, SearchField("test_text_field"))
    want = TextField("test_text_field", weight=1)
    assert have.args == want.args

    have = get_redis_field(BasePage, SearchField("test_integer_field"))
    want = NumericField("test_integer_field")
    assert have.args == want.args

    have = get_redis_field(BasePage, SearchField("test_boolean_field"))
    want = TagField("test_boolean_field")
    assert have.args == want.args


def test_RediSearchModelIndex():
    backend = RediSearchBackend({})
    index = RediSearchModelIndex(backend, "wagtail_Page", Page)
    assert index.document_key(123) == "wagtail_Page:123"


class SearchPages(TestCase):
    fixtures = ["pages.json"]

    def setUp(self, *args, **kwargs):
        call_command("update_index", *args, **kwargs)

    def test_full_text_search(self):
        great_gatsby = BasePage.objects.get(id=4)
        beautiful_damned = BasePage.objects.get(id=5)
        sun_rises = BasePage.objects.get(id=7)

        qs = BasePage.objects.search("fitzgerald")
        assert great_gatsby in qs
        assert beautiful_damned in qs
        assert sun_rises not in qs

        qs = BasePage.objects.search("fitzgerald", fields=["author"])
        assert great_gatsby in qs
        assert beautiful_damned in qs
        assert sun_rises not in qs

        qs = BasePage.objects.autocomplete("gats")
        assert great_gatsby in qs
        assert beautiful_damned not in qs
        assert sun_rises not in qs

        qs = BasePage.objects.exclude(id=great_gatsby.id).search("fitzgerald")
        assert great_gatsby not in qs
        assert beautiful_damned in qs
        assert sun_rises not in qs

        qs = BasePage.objects.filter(test_integer_field__gt=0).search("a")
        assert great_gatsby in qs
        assert beautiful_damned in qs
        assert sun_rises in qs

        qs = BasePage.objects.filter(test_integer_field__gte=300).search("a")
        assert great_gatsby not in qs
        assert beautiful_damned not in qs
        assert sun_rises in qs

        qs = (
            BasePage.objects.order_by("-test_integer_field").search(
                "page", order_by_relevance=False
            )
        ).queryset
        assert qs[0] == sun_rises
        assert qs[1] == beautiful_damned
        assert qs[2] == great_gatsby

        qs = (
            BasePage.objects.order_by("test_integer_field").search(
                "page", order_by_relevance=False
            )
        ).queryset
        assert qs[0] == great_gatsby
        assert qs[1] == beautiful_damned
        assert qs[2] == sun_rises
