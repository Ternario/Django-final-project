# Generated by Django 5.1.1 on 2025-02-11 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BookingDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='Start date')),
                ('end_date', models.DateField(verbose_name='End date')),
                ('is_confirmed', models.BooleanField(default=False, verbose_name='Is confirmed')),
                ('is_cancelled', models.BooleanField(default=False, verbose_name='Is cancelled')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Date updated')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
