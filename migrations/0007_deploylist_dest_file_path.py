# Generated by Django 2.1 on 2018-11-16 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0006_auto_20181115_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='deploylist',
            name='dest_file_path',
            field=models.CharField(max_length=1024, null=True),
        ),
    ]