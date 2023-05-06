# Generated by Django 4.1.7 on 2023-03-30 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_cafe_current_token_alter_cafe_next_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('full_address', models.CharField(max_length=100)),
                ('area', models.CharField(max_length=50)),
                ('tl', models.FloatField()),
                ('tr', models.FloatField()),
                ('bl', models.FloatField()),
                ('br', models.FloatField()),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.cafe')),
            ],
        ),
    ]
