from django.urls import path

from .views import HomeView, SuggestionAddView, search

urlpatterns = [
    path("", HomeView.as_view()),
    path("search/", search),
]
