# Generated by Django 3.1.2 on 2020-11-07 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('AdminChat', '0002_auto_20201107_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='AdminChat.message'),
        ),
    ]
