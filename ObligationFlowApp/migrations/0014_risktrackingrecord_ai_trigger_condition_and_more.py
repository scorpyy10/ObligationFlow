# Generated by Django 5.1.2 on 2024-11-13 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ObligationFlowApp', '0013_risktrackingrecord_document_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='risktrackingrecord',
            name='ai_trigger_condition',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='risktrackingrecord',
            name='responsible_parties',
            field=models.CharField(choices=[('John Smith', 'John Smith'), ('Sarah Watson', 'Sarah Watson'), ('Abhinav Kohli', 'Abhinav Kohli')], max_length=255),
        ),
    ]
