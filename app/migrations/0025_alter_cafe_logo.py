# Generated by Django 4.1.7 on 2023-05-06 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_remove_address_bl_remove_address_br_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cafe',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='cafe_logos'),
        ),
    ]
