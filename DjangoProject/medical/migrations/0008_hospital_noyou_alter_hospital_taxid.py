# Generated by Django 4.1.4 on 2022-12-19 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical", "0007_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="hospital",
            name="noyou",
            field=models.CharField(default="", max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name="hospital",
            name="taxid",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
