# Generated by Django 5.1.1 on 2024-11-02 01:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Apartments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('title', models.CharField(max_length=130, verbose_name='Apartments title')),
                ('description', models.TextField(max_length=250, validators=[django.core.validators.MinLengthValidator(40)], verbose_name='Apartments description')),
                ('city', models.CharField(max_length=100, verbose_name='City name')),
                ('post_code', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^[0-9]{0,6}$', 'Invalid postal code')])),
                ('street', models.CharField(max_length=120, verbose_name='Street name')),
                ('house_number', models.CharField(max_length=30, verbose_name='House number')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Price')),
                ('number_of_rooms', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)], verbose_name='Number of rooms')),
                ('apartment_area', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MaxValueValidator(400), django.core.validators.MinValueValidator(10)], verbose_name='Area of apartment')),
                ('number_of_beds', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)], verbose_name='Number of beds')),
                ('single_bed', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)], verbose_name='Number of single bed')),
                ('double_bed', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(0)], verbose_name='Number of double bed')),
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
            options={
                'ordering': ['-created_at'],
            },
        ),
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
    ]
