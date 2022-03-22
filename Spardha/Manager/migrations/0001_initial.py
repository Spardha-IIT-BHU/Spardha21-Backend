# Generated by Django 3.2.12 on 2022-03-22 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RightsSupport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'permissions': (('view_manager', 'View manager app'), ('export_all', 'Export all data'), ('export_game', 'Export game data'), ('export_user', 'Export user data')),
                'managed': False,
                'default_permissions': (),
            },
        ),
    ]
