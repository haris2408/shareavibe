# Generated by Django 4.1.7 on 2023-03-30 12:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_alter_customuser_cafe_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='customuser',
            old_name='cafe_id',
            new_name='cafe',
        ),
    ]
