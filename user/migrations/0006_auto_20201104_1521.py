# Generated by Django 3.1.2 on 2020-11-04 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_ride_payment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='location',
            field=models.CharField(blank=True, choices=[('aba', 'Aba'), ('umuahia', 'Umuahia'), ('port harcourt', 'Port Harcourt'), ('owerri', 'Owerri')], max_length=20, null=True, verbose_name='Present City'),
        ),
        migrations.AlterField(
            model_name='request',
            name='city',
            field=models.CharField(blank=True, choices=[('aba', 'Aba'), ('umuahia', 'Umuahia'), ('port harcourt', 'Port Harcourt'), ('owerri', 'Owerri')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='ride',
            name='payment_method',
            field=models.CharField(choices=[('cash', 'Cash'), ('card', 'Card')], default='card', max_length=6),
        ),
        migrations.AlterField(
            model_name='ride',
            name='payment_status',
            field=models.CharField(choices=[('unpaid', 'Unpaid'), ('paid', 'Paid')], default='unpaid', max_length=6),
        ),
        migrations.AlterField(
            model_name='ride',
            name='status',
            field=models.CharField(choices=[('unconfirmed', 'Unconfirmed'), ('waiting', 'Waiting'), ('ongoing', 'Ongoing'), ('completed', 'Completed')], default='unconfirmed', max_length=11),
        ),
    ]