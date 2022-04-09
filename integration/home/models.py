from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.search import index


class BasePage(Page):
    body = RichTextField()

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]
