# Generated by Django 3.2.15 on 2023-08-16 12:32

from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_firstname', models.CharField(max_length=80, verbose_name='Имя')),
                ('customer_lastname', models.CharField(max_length=80, verbose_name='Фамилия')),
                ('customer_phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='RU', verbose_name='Номер телефона')),
                ('customer_address', models.TextField(verbose_name='Адрес доставки')),
            ],
        ),
        migrations.CreateModel(
            name='ProductObject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='foodcartapp.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='foodcartapp.product', verbose_name='Товар')),
            ],
        ),
    ]
