from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.search import index


class BasePage(Page):
    body = RichTextField()
    test_text_field = models.TextField()
    test_char_field = models.CharField(max_length=100)
    test_email_field = models.EmailField()
    test_slug_field = models.SlugField()
    test_url_field = models.URLField()
    test_boolean_field = models.BooleanField()
    test_float_field = models.FloatField()
    test_integer_field = models.IntegerField()
    test_big_integer_field = models.BigIntegerField()
    test_positive_big_integer_field = models.PositiveBigIntegerField()
    test_positive_integer_field = models.PositiveIntegerField()
    test_positive_small_integer_field = models.PositiveSmallIntegerField()
    test_small_integer_field = models.SmallIntegerField()
    test_date_field = models.DateField()
    test_date_time_field = models.DateTimeField()
    test_time_field = models.TimeField()
    test_uuid_field = models.UUIDField()

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        FieldPanel("test_text_field"),
        FieldPanel("test_char_field"),
        FieldPanel("test_email_field"),
        FieldPanel("test_slug_field"),
        FieldPanel("test_url_field"),
        FieldPanel("test_boolean_field"),
        FieldPanel("test_float_field"),
        FieldPanel("test_integer_field"),
        FieldPanel("test_big_integer_field"),
        FieldPanel("test_positive_big_integer_field"),
        FieldPanel("test_positive_integer_field"),
        FieldPanel("test_positive_small_integer_field"),
        FieldPanel("test_small_integer_field"),
        FieldPanel("test_date_field"),
        FieldPanel("test_date_time_field"),
        FieldPanel("test_time_field"),
        FieldPanel("test_uuid_field"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
        index.SearchField("test_text_field"),
        index.SearchField("test_char_field"),
        index.SearchField("test_email_field"),
        index.SearchField("test_slug_field"),
        index.SearchField("test_url_field"),
        index.SearchField("test_boolean_field"),
        index.SearchField("test_float_field"),
        index.SearchField("test_integer_field"),
        index.SearchField("test_big_integer_field"),
        index.SearchField("test_positive_big_integer_field"),
        index.SearchField("test_positive_integer_field"),
        index.SearchField("test_positive_small_integer_field"),
        index.SearchField("test_small_integer_field"),
        index.SearchField("test_date_field"),
        index.SearchField("test_date_time_field"),
        index.SearchField("test_time_field"),
        index.SearchField("test_uuid_field"),
    ]
