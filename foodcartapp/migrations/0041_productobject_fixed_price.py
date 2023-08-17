# Generated by Django 3.2.15 on 2023-08-17 08:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_rename_count_productobject_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='productobject',
            name='fixed_price',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=5, validators=[django.core.validators.MinValueValidator(0, 0)], verbose_name='Стоимость позиции'),
            preserve_default=False,
        ),
    ]
