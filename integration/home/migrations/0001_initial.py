# Generated by Django 3.2.12 on 2022-04-11 17:46

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0066_collection_management_permissions"),
    ]

    operations = [
        migrations.CreateModel(
            name="BasePage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                ("body", wagtail.core.fields.RichTextField()),
                ("test_text_field", models.TextField()),
                ("test_char_field", models.CharField(max_length=100)),
                ("test_email_field", models.EmailField(max_length=254)),
                ("test_slug_field", models.SlugField()),
                ("test_url_field", models.URLField()),
                ("test_boolean_field", models.BooleanField()),
                ("test_float_field", models.FloatField()),
                ("test_integer_field", models.IntegerField()),
                ("test_big_integer_field", models.BigIntegerField()),
                ("test_positive_big_integer_field", models.PositiveBigIntegerField()),
                ("test_positive_integer_field", models.PositiveIntegerField()),
                (
                    "test_positive_small_integer_field",
                    models.PositiveSmallIntegerField(),
                ),
                ("test_small_integer_field", models.SmallIntegerField()),
                ("test_date_field", models.DateField()),
                ("test_date_time_field", models.DateTimeField()),
                ("test_time_field", models.TimeField()),
                ("test_uuid_field", models.UUIDField()),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
