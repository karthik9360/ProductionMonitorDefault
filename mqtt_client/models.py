from django.db import models

class MqttSettings(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return f'MQTT Settings for {self.host}'

class LogData(models.Model):
    date = models.DateField()
    time = models.TimeField()
    received_data = models.TextField()
    protocol = models.CharField(max_length=50)
    topic_api = models.CharField(max_length=255)
    unique_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'LogData {self.unique_id}'

class DeviceDetails(models.Model):
    device_token = models.CharField(max_length=255)
    sub_topic = models.CharField(max_length=255, blank=True, null=True)
    pub_topic = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.device_token

class MachineDetails(models.Model):
    machine_id = models.CharField(max_length=255)
    machine_name = models.CharField(max_length=255)

    def __str__(self):
        return self.machine_id

class DeviceData(models.Model):
    date = models.DateField()
    time = models.TimeField()
    data = models.JSONField()
    device_id = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)
    protocol = models.CharField(max_length=50)
    topic_api = models.CharField(max_length=255)
    log_data_id = models.ForeignKey(LogData, on_delete=models.CASCADE)

    def __str__(self):
        return f'DeviceData {self.device_id}'

class MachineData(models.Model):
    date = models.DateField()
    time = models.TimeField()
    machine_id = models.ForeignKey(MachineDetails, on_delete=models.CASCADE)
    data = models.JSONField()
    device_id = models.ForeignKey(DeviceDetails, on_delete=models.CASCADE)
    data_id = models.ForeignKey(LogData, on_delete=models.CASCADE)

    def __str__(self):
        return f'MachineData {self.machine_id}'

class ProductionData(models.Model):
    machine_id = models.CharField(max_length=255)
    production_count = models.IntegerField()
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f'ProductionData {self.machine_id}'
