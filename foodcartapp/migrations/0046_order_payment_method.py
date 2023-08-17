# Generated by Django 3.2.15 on 2023-08-17 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0045_auto_20230817_1138'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_method',
            field=models.IntegerField(choices=[(0, 'Не определён'), (1, 'Электронно'), (2, 'Наличностью')], db_index=True, default=0, verbose_name='Метод оплаты'),
        ),
    ]