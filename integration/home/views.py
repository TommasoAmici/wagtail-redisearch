from http.client import HTTPResponse

from django.shortcuts import render
from django.views.generic.base import TemplateView, View
from redis.commands.search.suggestion import Suggestion
from wagtail.core.models import Page
from wagtail.search.backends import get_search_backend
from wagtail_redisearch.backend import RediSearchBackend


class HomeView(TemplateView):
    template_name = "home/home.html"


def search(request):
    search_query = request.GET.get("query", None)
    if search_query:
        if request.headers.get("Hx-Trigger") is None:
            search_results = Page.objects.live().search(search_query)
        else:
            search_results = Page.objects.live().autocomplete(search_query)
    else:
        search_results = Page.objects.none()

    # Render template
    return render(
        request,
        "home/search_results.html",
        {
            "search_results": search_results,
            "search_query": search_query,
        },
    )

