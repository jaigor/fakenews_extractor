# Generated by Django 3.1.4 on 2021-05-03 10:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0004_auto_20210419_1456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='text',
            field=models.CharField(max_length=256, unique=True),
        ),
        migrations.AddField(
            model_name='query',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]