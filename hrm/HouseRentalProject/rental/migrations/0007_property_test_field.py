# Generated by Django 4.2.3 on 2024-10-30 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0006_property_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='test_field',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
