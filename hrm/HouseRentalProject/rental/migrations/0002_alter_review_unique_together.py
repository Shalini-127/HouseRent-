# Generated by Django 5.1.2 on 2024-10-28 21:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together={('user', 'property')},
        ),
    ]
