# Generated by Django 3.2.15 on 2024-10-15 09:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ObligationFlowApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='description',
        ),
        migrations.RemoveField(
            model_name='document',
            name='folder',
        ),
        migrations.RemoveField(
            model_name='document',
            name='ground_truth',
        ),
        migrations.RemoveField(
            model_name='document',
            name='thumbnail',
        ),
        migrations.AddField(
            model_name='document',
            name='contract_model',
            field=models.CharField(db_index=True, default='default_value', max_length=100),
        ),
        migrations.AddField(
            model_name='document',
            name='vendor',
            field=models.CharField(db_index=True, default='default_vendor', max_length=100),
        ),
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to='documents/', validators=[django.core.validators.FileExtensionValidator(['pdf', 'docx'])]),
        ),
        migrations.DeleteModel(
            name='Folder',
        ),
    ]
