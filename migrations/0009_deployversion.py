# Generated by Django 2.1 on 2018-11-19 03:07

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('deploy', '0008_deploylist_backup_file_path'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeployVersion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('version_path', models.CharField(max_length=1024, null=True)),
                ('symbol', models.CharField(max_length=64)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]