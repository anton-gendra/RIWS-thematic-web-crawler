# Generated by Django 4.1.1 on 2022-11-15 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Click',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clicks', models.IntegerField(default=0)),
                ('component', models.CharField(max_length=256)),
            ],
        ),
    ]
