# Generated by Django 4.1.4 on 2022-12-19 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("medical", "0008_hospital_noyou_alter_hospital_taxid"),
    ]

    operations = [
        migrations.CreateModel(
            name="test",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tax", models.CharField(max_length=20, unique=True)),
            ],
        ),
    ]
