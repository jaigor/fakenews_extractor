# Generated by Django 3.1.4 on 2021-05-03 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0009_auto_20210503_1540'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='tweet_id',
            new_name='tweets',
        ),
    ]
