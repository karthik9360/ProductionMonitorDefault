# Generated by Django 5.0.7 on 2024-08-02 07:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DeviceDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_token', models.CharField(max_length=255)),
                ('sub_topic', models.CharField(blank=True, max_length=255, null=True)),
                ('pub_topic', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LogData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('received_data', models.TextField()),
                ('protocol', models.CharField(max_length=50)),
                ('topic_api', models.CharField(max_length=255)),
                ('unique_id', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MachineDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_id', models.CharField(max_length=255)),
                ('machine_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MqttSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('host', models.CharField(max_length=255)),
                ('port', models.IntegerField()),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machine_id', models.CharField(max_length=255)),
                ('production_count', models.IntegerField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DeviceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('data', models.JSONField()),
                ('protocol', models.CharField(max_length=50)),
                ('topic_api', models.CharField(max_length=255)),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt_client.devicedetails')),
                ('log_data_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt_client.logdata')),
            ],
        ),
        migrations.CreateModel(
            name='MachineData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('data', models.JSONField()),
                ('data_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt_client.logdata')),
                ('device_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt_client.devicedetails')),
                ('machine_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mqtt_client.machinedetails')),
            ],
        ),
    ]
