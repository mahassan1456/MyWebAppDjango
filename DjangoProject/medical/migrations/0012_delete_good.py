# Generated by Django 4.1.4 on 2022-12-19 14:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("medical", "0011_rename_tax_good_tax_id"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Good",
        ),
    ]
