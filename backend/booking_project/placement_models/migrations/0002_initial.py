# Generated by Django 5.1.1 on 2024-11-02 01:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('placement_models', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='apartments',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Owner', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='apartments',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Apartments', to='placement_models.categories', verbose_name='Category'),
        ),
        migrations.AddConstraint(
            model_name='apartments',
            constraint=models.CheckConstraint(condition=models.Q(('single_bed__isnull', False), ('double_bed__isnull', False), _connector='OR'), name="Both fields can't be zero"),
        ),
    ]