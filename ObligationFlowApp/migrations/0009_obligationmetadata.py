# Generated by Django 5.1.2 on 2024-11-05 04:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ObligationFlowApp', '0008_alter_document_file_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObligationMetadata',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obligation_id', models.IntegerField()),
                ('document_id', models.IntegerField()),
                ('metadata', models.JSONField(blank=True, default=dict, null=True)),
            ],
        ),
    ]
