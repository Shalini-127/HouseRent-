# Generated by Django 5.1.2 on 2024-10-28 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0002_alter_review_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='image',
            field=models.ImageField(default='default.jpg', upload_to='property_images/'),
            preserve_default=False,
        ),
    ]
