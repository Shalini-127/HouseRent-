# Generated by Django 5.1.2 on 2024-10-30 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0003_property_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(default=5),
        ),
    ]