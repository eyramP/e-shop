# Generated by Django 4.2.11 on 2024-03-25 19:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0003_review"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product", name="ratings", field=models.IntegerField(default=0),
        ),
    ]
