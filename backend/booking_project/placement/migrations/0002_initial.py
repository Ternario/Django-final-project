# Generated by Django 5.1.1 on 2024-11-18 02:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('placement', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='placement',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Owner', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='location',
            name='placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placement_location', to='placement.placement', verbose_name='placement'),
        ),
        migrations.AddField(
            model_name='placementdetails',
            name='placement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='placement_details', to='placement.placement'),
        ),
        migrations.AddConstraint(
            model_name='placement',
            constraint=models.CheckConstraint(condition=models.Q(('single_bed__isnull', False), ('double_bed__isnull', False), _connector='OR'), name="Both fields can't be zero"),
        ),
    ]
