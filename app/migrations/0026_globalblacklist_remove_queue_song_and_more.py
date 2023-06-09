# Generated by Django 4.1.7 on 2023-05-25 21:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_alter_cafe_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalBlacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_name', models.CharField(max_length=255, null=True)),
                ('song_link', models.CharField(max_length=255)),
            ],
        ),
        migrations.RemoveField(
            model_name='queue',
            name='song',
        ),
        migrations.AddField(
            model_name='customuser',
            name='is_login',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='CafeBlacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('song_name', models.CharField(max_length=255, null=True)),
                ('song_link', models.CharField(max_length=255)),
                ('cafe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.cafe')),
            ],
        ),
    ]
