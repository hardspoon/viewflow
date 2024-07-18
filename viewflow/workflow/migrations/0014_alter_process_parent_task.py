# Generated by Django 5.0.1 on 2024-07-11 05:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("viewflow", "0013_process_seed_content_type_process_seed_object_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="process",
            name="parent_task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subprocesses",
                to="viewflow.task",
            ),
        ),
    ]