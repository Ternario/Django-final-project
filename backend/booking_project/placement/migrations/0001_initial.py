# Generated by Django 5.1.1 on 2025-02-11 23:18

import booking_project.placement.models.placement_image
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Category')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(blank=True, max_length=155, verbose_name='Country name')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='City name')),
                ('post_code', models.CharField(blank=True, max_length=6, validators=[django.core.validators.RegexValidator('^[0-9]{0,6}$', 'Invalid postal code')])),
                ('street', models.CharField(blank=True, max_length=155, verbose_name='Street name')),
                ('house_number', models.CharField(blank=True, max_length=30, verbose_name='House number')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Date created')),
            ],
        ),
        migrations.CreateModel(
            name='PlacementDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pets', models.BooleanField(default=False, verbose_name='Pets friendly')),
                ('free_wifi', models.BooleanField(default=False, verbose_name='Free wifi')),
                ('smoking', models.BooleanField(default=False, verbose_name='Smoking allowed')),
                ('parking', models.BooleanField(default=False, verbose_name='Parking space')),
                ('room_service', models.BooleanField(default=False, verbose_name='Room service')),
                ('front_desk_allowed_24', models.BooleanField(default=False, verbose_name='24-hour front desk')),
                ('free_cancellation', models.BooleanField(default=False, verbose_name='Free cancellation')),
                ('balcony', models.BooleanField(default=False, verbose_name='Balcony')),
                ('air_conditioning', models.BooleanField(default=False, verbose_name='Air conditioning')),
                ('washing_machine', models.BooleanField(default=False, verbose_name='Washing machine')),
                ('kitchenette', models.BooleanField(default=False, verbose_name='Kitchenette')),
                ('tv', models.BooleanField(default=False, verbose_name='Tv')),
                ('coffee_tee_maker', models.BooleanField(default=False, verbose_name='Coffee/Tea maker')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Date updated')),
            ],
        ),
        migrations.CreateModel(
            name='PlacementImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('placement_image', models.ImageField(blank=True, null=True, upload_to=booking_project.placement.models.placement_image.PlacementImage.upload_to, verbose_name='Placement images')),
            ],
        ),
        migrations.CreateModel(
            name='Placement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=130, verbose_name='Apartments title')),
                ('description', models.TextField(max_length=1000, validators=[django.core.validators.MinLengthValidator(40)], verbose_name='Apartments description')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('number_of_rooms', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)], verbose_name='Number of rooms')),
                ('placement_area', models.FloatField(default=0)),
                ('number_of_beds', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)], verbose_name='Number of beds')),
                ('single_bed', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)], verbose_name='Number of single bed')),
                ('double_bed', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)], verbose_name='Number of double bed')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Date updated')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Is deleted')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='Apartments', to='placement.categories', verbose_name='Category')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
