# Generated by Django 3.2.15 on 2023-08-19 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_alter_order_restaurant'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ProductObject',
            new_name='OrderedProduct',
        ),
    ]
