from wagtail.search.backends.base import (
    BaseSearchBackend,
    BaseSearchResults,
    EmptySearchResults,
)


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

class RediSearchBackend(BaseSearchBackend):
    index_name = "wagtail"

    def __init__(self, params):
        super(RediSearchBackend, self).__init__(params)

    def get_index_for_model(self, model):
        # Split models up into separate indices based on their root model.
        # For example, all page-derived models get put together in one index,
        # while images and documents each have their own index.
        root_model = get_model_root(model)
        index_name = (
            f"{self.index_name}__{root_model._meta.app_label}_{root_model.__name__}"
        )

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



SearchBackend = RediSearchBackend
