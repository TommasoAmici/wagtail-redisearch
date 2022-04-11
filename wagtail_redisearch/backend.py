from datetime import datetime
from typing import List, Union
from uuid import UUID

import redis
from django.db import models
from django.db.models.lookups import (
    Exact,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Lookup,
)
from django.db.models.sql.where import SubqueryConstraint, WhereNode
from redis import Redis
from redis.commands.search.field import NumericField, TagField, TextField
from redis.commands.search.query import Query
from redis.commands.search.querystring import DistjunctUnion, IntersectNode, UnionNode
from wagtail.search.backends.base import (
    BaseSearchBackend,
    BaseSearchResults,
    EmptySearchResults,
    FilterError,
    OrderByFieldError,
    SearchFieldError,
)
from wagtail.search.index import (
    AutocompleteField,
    FilterField,
    RelatedFields,
    SearchField,
    class_is_indexed,
)
from wagtail.search.query import And, Boost, MatchAll, Not, Or, Phrase, PlainText

WagtailQuery = Union[str, PlainText, Phrase, And, Or, Not, MatchAll]
WagtailSearchFields = Union[List[str], None]


def get_model_root(model):
    """
    This function finds the root model for any given model. The root model is
    the highest concrete model that it descends from. If the model doesn't
    descend from another concrete model then the model is it's own root model so
    it is returned.

    Examples:
    >>> get_model_root(wagtail.core.Page) # doctest: +SKIP
    wagtailcore.Page
    >>> get_model_root(myapp.HomePage) # doctest: +SKIP
    wagtailcore.Page
    >>> get_model_root(wagtailimages.Image) # doctest: +SKIP
    wagtailimages.Image
    """
    if model._meta.parents:
        parent_model = list(model._meta.parents.items())[0][0]
        return get_model_root(parent_model)

    return model


redis_field_from_type = {
    "TextField": TextField,
    "CharField": TextField,
    "EmailField": TextField,
    "SlugField": TextField,
    "URLField": TextField,
    "AutoField": NumericField,
    "SmallAutoField": NumericField,
    "BigAutoField": NumericField,
    "BooleanField": TagField,
    "FloatField": NumericField,
    "IntegerField": NumericField,
    "BigIntegerField": NumericField,
    "PositiveBigIntegerField": NumericField,
    "PositiveIntegerField": NumericField,
    "PositiveSmallIntegerField": NumericField,
    "SmallIntegerField": NumericField,
    "DateField": NumericField,
    "DateTimeField": NumericField,
    "TimeField": NumericField,
    "UUIDField": TextField,
}


def get_redis_field(
    model, field, sortable=False, no_index=False
) -> Union[TextField, NumericField]:
    field_type = field.get_type(model)
    redis_field = redis_field_from_type.get(field_type, None)
    if redis_field is TextField:
        weight = 1
        try:
            if field.boost is not None:
                weight = field.boost
        except AttributeError:
            pass
        return TextField(
            field.field_name,
            weight=weight,
            sortable=sortable,
            no_index=no_index,
        )
    elif redis_field is NumericField:
        return NumericField(
            field.field_name,
            sortable=sortable,
            no_index=no_index,
        )
    elif redis_field is TagField:
        return TagField(field.field_name)
    else:
        raise SearchFieldError(
            f"Field type {field_type} is not yet mapped in wagtail-redisearch"
        )


def value_to_redis(value) -> Union[str, int]:
    """
    Convert value to a redis-compatible type
    >>> value_to_redis(1)
    1
    >>> value_to_redis(True)
    1
    >>> value_to_redis("wagtail")
    'wagtail'
    >>> value_to_redis(["1", "2", "3"])
    '1, 2, 3'
    >>> value_to_redis([1, 2, 3])
    '1, 2, 3'
    >>> from datetime import timezone
    >>> value_to_redis(datetime(2020, 1, 1, tzinfo=timezone.utc))
    1577836800.0
    >>> value_to_redis(UUID("5343fec8-de40-47ff-ac3b-65374f87dc61"))
    '5343fec8-de40-47ff-ac3b-65374f87dc61'
    >>> value_to_redis(None)
    ''
    """
    if isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return int(value)
    elif isinstance(value, int):
        return value
    elif isinstance(value, list):
        try:
            return ", ".join(value)
        except TypeError:
            return ", ".join([str(v) for v in value])
    elif isinstance(value, datetime):
        return value.timestamp()
    elif isinstance(value, UUID):
        return str(value)
    elif value is None:
        return ""
    else:
        raise ValueError(f"Cannot convert type {str(type(value))} to Redis type")


class RediSearchModelIndex:
    def __init__(self, backend, name: str, model):
        self.backend = backend
        self.name = name
        self.client: Redis = backend.client
        self.model = model
        self.fields = model.search_fields

    def document_key(self, document_id):
        return f"{self.name}:{document_id}"

    @property
    def ft(self):
        return self.client.ft(self.name)

    def create(self):
        mapping = {"wagtail_id": NumericField("wagtail_id")}
        try:
            self.ft.create_index(fields=mapping.values())
            return self
        except redis.exceptions.ResponseError as e:
            if str(e) == "Index already exists":
                return self
            else:
                raise e

    def delete(self):
        try:
            self.ft.dropindex(delete_documents=True)
        except redis.exceptions.ResponseError as e:
            # if the index doesn't exist continue
            if str(e) == "Unknown Index name":
                pass

    def add_model(self, model):
        search_fields = model.get_searchable_search_fields()
        filterable_fields = model.get_filterable_search_fields()

        for field in search_fields:
            if isinstance(field, SearchField):
                field = get_redis_field(model, field)
                try:
                    self.ft.alter_schema_add(fields=[field])
                except redis.exceptions.ResponseError as e:
                    if "Duplicate field in schema" in str(e):
                        pass

        for field in filterable_fields:
            if isinstance(field, FilterField):
                info = self.ft.info()
                field_name_b = field.field_name.encode()
                field_exists = any(
                    [attr for attr in info["attributes"] if attr[1] == field_name_b]
                )
                if field_exists:
                    continue
                else:
                    field = TagField(field.field_name)
                    self.ft.alter_schema_add(fields=[field])

    def add_item(self, item, fields):
        # Make sure the object can be indexed
        if not class_is_indexed(item.__class__):
            return

        mapping = {"wagtail_id": item.id}
        for field in fields:
            if (
                isinstance(field, SearchField)
                or isinstance(field, FilterField)
                or isinstance(field, AutocompleteField)
            ):
                value = field.get_value(item)
                mapping[field.field_name] = value_to_redis(value)
            elif isinstance(field, RelatedFields):
                # TODO RelatedFields
                pass
        self.client.hset(self.document_key(item.id), mapping=mapping)

    def add_items(self, model, items):
        if not class_is_indexed(model):
            return
        for item in items:
            self.add_item(item, model.search_fields)

    def delete_item(self, item):
        # Make sure the object can be indexed
        if not class_is_indexed(item.__class__):
            return
        self.client.delete(self.document_key(item.id))

    def reset(self):
        """Deletes index and re-creates it"""
        self.delete()
        self.create()


class RediSearchIndexRebuilder:
    index: RediSearchModelIndex

    def __init__(self, index):
        self.index = index

    def start(self):
        return self.index.create()

    def finish(self):
        pass


def build_query_string_autocomplete(
    query: PlainText, queryset: models.QuerySet, fields: WagtailSearchFields
) -> str:
    # if no fields are explicitly provided, search all autocomplete fields
    if fields is None:
        fields = [a.field_name for a in queryset.model.get_autocomplete_search_fields()]
    query_string = f"@{build_filter_fields(fields)}:{query.query_string.rstrip()}*"
    return query_string


def build_filter_fields(fields: List[str]) -> str:
    """
    Returns union of fields to restrict search to those fields.

    >>> build_filter_fields(["title", "search_description"])
    'title|search_description'
    """
    return UnionNode(*fields).to_string(with_parens=False)


def build_query_string(
    query: WagtailQuery,
    queryset: models.QuerySet,
    fields: WagtailSearchFields,
    autocomplete=False,
) -> str:
    """
    Builds a query that conforms to the RediSearch query syntax.
    https://redis.io/docs/stack/search/reference/query_syntax/
    """
    if isinstance(query, PlainText):
        if autocomplete:
            return build_query_string_autocomplete(query, queryset, fields)

        if query.operator == "or":
            query_string = UnionNode(*query.query_string.split()).to_string()
        else:
            query_string = query.query_string
        if fields is None:
            return query_string
        return f"@{build_filter_fields(fields)}:{query_string}"

    elif isinstance(query, Phrase):
        if fields is None:
            return f'"{query.query_string}"'
        else:
            return f'@{build_filter_fields(fields)}:"{query.query_string}"'

    elif isinstance(query, And):
        return IntersectNode(
            build_query_string(query.subqueries[0], queryset, fields),
            build_query_string(query.subqueries[1], queryset, fields),
        ).to_string()

    elif isinstance(query, Or):
        return UnionNode(
            build_query_string(query.subqueries[0], queryset, fields),
            build_query_string(query.subqueries[1], queryset, fields),
        ).to_string()

    elif isinstance(query, Boost):
        query_string = build_query_string(query.subquery, queryset, fields)
        return f"{query_string} => {{ $weight: {query.boost} }}"

    elif isinstance(query, Not):
        query_string = build_query_string(query.subquery, queryset, fields)
        return DistjunctUnion(query_string).to_string()

    else:
        raise NotImplementedError(
            "`%s` is not supported by the RediSearch search backend."
            % query.__class__.__name__
        )


def check_fields(
    fields: WagtailSearchFields, queryset: models.QuerySet, autocomplete: bool
):
    """Checks if fields are currently indexed, otherwise raises a SearchFieldError"""
    if fields is None:
        return

    if autocomplete:
        searchable_fields = queryset.model.get_autocomplete_search_fields()
        error_msg = "index.AutocompleteField"
    else:
        searchable_fields = queryset.model.get_searchable_search_fields()
        error_msg = "index.SearchField"

    allowed_fields = {field.field_name for field in searchable_fields}

    for field_name in fields:
        if field_name not in allowed_fields:
            raise SearchFieldError(
                f'Cannot search with field "{field_name}". Please add '
                f"{error_msg}('{field_name}') to {queryset.model.__name__}.search_fields.",
                field_name=field_name,
            )


def get_filterable_field(queryset: models.QuerySet, field_name: str):
    return dict(
        (field.get_attname(queryset.model), field)
        for field in queryset.model.get_filterable_search_fields()
    ).get(field_name, None)


def build_sort_by(queryset: models.QuerySet, order_by_relevance=True) -> str:
    if order_by_relevance:
        return ""

    sort_by = []
    for field_name in queryset.query.order_by:
        ascending = False

        if field_name.startswith("-"):
            ascending = True
            field_name = field_name[1:]

        field = get_filterable_field(queryset, field_name)

        if field is None:
            raise OrderByFieldError(
                f'Cannot sort search results with field "{field_name}". Please add '
                f'index.FilterField("{field_name}") to {queryset.model.__name__}.search_fields.',
                field_name=field_name,
            )

        sort_by.append((field_name, ascending))
    return " ".join([f"SORTBY {s[0]} {'ASC' if s[1] else 'DESC'}" for s in sort_by])


def build_filters(lookup: Lookup, negated=False) -> str:
    if isinstance(lookup, WhereNode):
        children = []
        for child in lookup.children:
            try:
                child_negated = child.negated
            except AttributeError:
                child_negated = False
            children.append(build_filters(child, negated=child_negated or negated))

        connector = lookup.connector
        if connector == "AND":
            return " ".join(children)
        elif connector == "OR":
            return UnionNode(*children).to_string()
        else:
            raise NotImplementedError(f"Connector {connector} is not supported yet")

    field: models.Field = lookup.lhs.field
    field_name = field.name
    if field_name == "id":
        field_name = "wagtail_id"

    field_type = field.get_internal_type()
    redis_field = redis_field_from_type.get(field_type)
    if redis_field is None:
        raise NotImplementedError(
            f"{field_type} is not yet supported by wagtail-redisearch"
        )

    value = value_to_redis(lookup.rhs)

    if isinstance(lookup, Exact):
        # for NumericField specify value as both min and max
        if redis_field == NumericField:
            value = f"[{value} {value}]"
        # exact searches shouldn't perform a search, so wrap the value in curly braces
        else:
            value = f"{{{value}}}"

    elif isinstance(lookup, GreaterThan):
        if redis_field != NumericField:
            raise FilterError(f"{field_type} is not a numeric field")
        value = f"[({value} inf]"

    elif isinstance(lookup, GreaterThanOrEqual):
        if redis_field != NumericField:
            raise FilterError(f"{field_type} is not a numeric field")
        value = f"[{value} inf]"

    elif isinstance(lookup, LessThan):
        if redis_field != NumericField:
            raise FilterError(f"{field_type} is not a numeric field")
        value = f"[-inf ({value}]"

    elif isinstance(lookup, LessThanOrEqual):
        if redis_field != NumericField:
            raise FilterError(f"{field_type} is not a numeric field")
        value = f"[-inf {value}]"

    elif isinstance(lookup, SubqueryConstraint):
        raise FilterError(
            "Could not apply filter on search results: Subqueries are not allowed."
        )
    else:
        raise FilterError(
            f"Could not apply filter on search results: Unknown where node: {str(type(lookup))}"
        )

    if negated:
        return f"-@{field_name}:{value}"
    else:
        return f"@{field_name}:{value}"


def build_query(
    query: WagtailQuery,
    fields: WagtailSearchFields,
    queryset: models.QuerySet,
    order_by_relevance=False,
    autocomplete=False,
) -> Query:
    """Builds query for RediSearch"""

    check_fields(fields, queryset, autocomplete)

    return Query(
        " ".join(
            [
                build_query_string(query, queryset, fields, autocomplete),
                build_sort_by(queryset, order_by_relevance),
                build_filters(queryset.query.where),
            ]
        )
    )


class RediSearchResults(BaseSearchResults):
    def __init__(
        self,
        query: WagtailQuery,
        queryset: models.QuerySet,
        fields: WagtailSearchFields,
        index: RediSearchModelIndex,
        order_by_relevance: bool,
        autocomplete: bool,
    ):
        self.query = query
        self.queryset = queryset
        self.fields = fields
        self.index = index
        self.order_by_relevance = order_by_relevance
        self.autocomplete = autocomplete
        self.start = 0
        self.stop = None
        self._results_cache = None
        self._count_cache = None
        self._score_field = None

    def _clone(self):
        klass = self.__class__
        new = klass(
            self.query,
            self.queryset,
            self.fields,
            self.index,
            self.order_by_relevance,
            self.autocomplete,
        )
        new.start = self.start
        new.stop = self.stop
        new._score_field = self._score_field
        return new

    def _do_search(self):
        query = build_query(
            self.query,
            self.fields,
            self.queryset,
            self.order_by_relevance,
            self.autocomplete,
        )
        results = self.index.ft.search(query)
        return self.queryset.filter(id__in=[doc.wagtail_id for doc in results.docs])

    def _do_count(self):
        return self._do_search().count()


class RediSearchBackend(BaseSearchBackend):
    index_name = "wagtail"
    rebuilder_class = RediSearchIndexRebuilder
    client: Redis
    DEFAULT_OPERATOR = "and"

    def __init__(self, params):
        super(RediSearchBackend, self).__init__(params)

        self.index_name = params.pop("INDEX", "wagtail")

        host = params.pop("HOST", "127.0.0.1")
        port = params.pop("PORT", 6379)
        self.client = Redis(host=host, port=port, db=0, **params)

    def get_index_for_model(self, model):
        # Split models up into separate indices based on their root model.
        # For example, all page-derived models get put together in one index,
        # while images and documents each have their own index.
        root_model = get_model_root(model)
        index_name = (
            f"{self.index_name}__{root_model._meta.app_label}_{root_model.__name__}"
        )
        return RediSearchModelIndex(self, index_name, model)

    def search(
        self,
        query: Union[str, WagtailQuery],
        model_or_queryset: models.QuerySet,
        fields=None,
        operator=None,
        order_by_relevance=True,
        # partial matching in search() will be completely removed in a future release
        # https://docs.wagtail.org/en/stable/releases/2.15.html#search-method-partial-match-future-deprecation
        partial_match=False,
        autocomplete=False,
    ):
        # Find model/queryset
        if isinstance(model_or_queryset, models.QuerySet):
            model = model_or_queryset.model
            queryset = model_or_queryset
        else:
            model = model_or_queryset
            queryset = model_or_queryset.objects.all()

        # Model must be a class that is in the index
        if not class_is_indexed(model):
            return EmptySearchResults()

        # Check that there's still a query string after the clean up
        if query == "":
            return EmptySearchResults()

        if isinstance(query, str):
            if not autocomplete:
                # prevent users from (ab)using globbing and fuzzy matching
                query = query.replace("*", "").replace("%", "")
            query = PlainText(query, operator=operator or self.DEFAULT_OPERATOR)

        return RediSearchResults(
            query,
            queryset,
            fields,
            self.get_index_for_model(model),
            order_by_relevance,
            autocomplete,
        )

    def autocomplete(self, *args, **kwargs):
        return self.search(*args, **kwargs, autocomplete=True)


SearchBackend = RediSearchBackend
