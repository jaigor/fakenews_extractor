# Generated by Django 3.1.4 on 2021-04-19 12:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0003_auto_20210413_2341'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='tweet_id',
            field=models.ManyToManyField(blank=True, to='twitter.Tweet'),
        ),
        migrations.AlterField(
            model_name='tweet',
            name='author_id',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='twitter.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('text', models.CharField(max_length=256, primary_key=True, serialize=False, unique=True)),
                ('tweet_id', models.ManyToManyField(blank=True, to='twitter.Tweet')),
            ],
        ),
    ]