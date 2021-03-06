# Generated by Django 3.2.5 on 2021-07-14 11:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import static_content.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Premier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the Premier', max_length=255)),
                ('url', models.SlugField(help_text='Relative url of the Premier', max_length=255, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('logo', models.ImageField(blank=True, help_text='The logo of the Premier', null=True, upload_to=static_content.utils.upload_to)),
                ('is_active', models.BooleanField(default=False, help_text='Designates whether to display Premier on web-site or not')),
                ('premier_at', models.DateTimeField(help_text='The time when the premier is released')),
                ('last_updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, help_text='The user that added the premier', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'premiers',
            },
        ),
    ]
