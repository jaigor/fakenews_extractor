# Generated by Django 3.1.4 on 2021-05-03 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0005_auto_20210503_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='lang',
            field=models.CharField(max_length=5, null=True),
        ),
    ]