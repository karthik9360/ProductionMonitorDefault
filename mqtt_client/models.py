from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class MqttSettings(models.Model):
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return f'MQTT Settings for {self.host}'

class LogData(models.Model):
    unique_id = models.CharField(max_length=255, unique=True)
    date = models.DateField()
    time = models.TimeField()
    received_data = models.JSONField()
    protocol = models.CharField(max_length=50)
    topic_api = models.CharField(max_length=255)

    def __str__(self):
        return f'LogData {self.unique_id}'

class DeviceDetails(models.Model):
    PROTOCOL_CHOICES = [
        ('mqtt', 'MQTT'),
        ('http', 'HTTP')
    ]

    device_name = models.CharField(max_length=45, blank=False, null=True)
    device_token = models.CharField(max_length=100, blank=False, unique=True)
    hardware_version = models.CharField(max_length=10, null=True, blank=True)
    software_version = models.CharField(max_length=10, null=True, blank=True)
    protocol = models.CharField(max_length=10, blank=False, choices=PROTOCOL_CHOICES, null=True)
    pub_topic = models.CharField(max_length=100, null=True, blank=True)
    sub_topic = models.CharField(max_length=100, null=True, blank=True)
    api_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.device_name

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
    
class ShiftTiming(models.Model):
    # _id=models.AutoField(primary_key=True, default=1)
    shift_number = models.IntegerField(blank=False, null=False ,default=1)  # Required field
    start_time = models.TimeField(blank=True, null=True)  # Optional field
    end_time = models.TimeField(blank=True, null=True)  # Optional field
    shift_name = models.CharField(max_length=45, blank=True, null=True)  # Optional field
    create_date_time = models.DateTimeField(auto_now_add=True)
    update_date_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.shift_number)  # Convert to string
    
class MqttSettings(models.Model):
    QOS_CHOICES = [
        (0, 'At most once (0)'),
        (1, 'At least once (1)'),
        (2, 'Exactly once (2)'),
    ]

    server_name_alias = models.CharField(max_length=45, blank=False, default="default")
    host = models.CharField(max_length=45, blank=False)
    port = models.IntegerField(blank=False)
    username = models.CharField(max_length=45, blank=True)
    password = models.CharField(max_length=45, blank=True)
    qos = models.IntegerField(choices=QOS_CHOICES, default=0, blank=False)
    keepalive = models.IntegerField(default=60, blank=False)
    pub_topic = models.CharField(max_length=255, default='default/pub/topic', blank=False)  # added field with default
    sub_topic = models.CharField(max_length=255, default='default/sub/topic', blank=False)  # added field with default

    def save(self, *args, **kwargs):
        if not self.pk and MqttSettings.objects.exists():
            raise ValidationError("There can be only one MqttSettings instance")
        return super(MqttSettings, self).save(*args, **kwargs)

    def __str__(self):
        return self.server_name_alias

    class Meta:
        verbose_name = "Mqtt"
        verbose_name_plural = "Mqtt"

class HttpsSettings(models.Model):
    auth_token = models.CharField(max_length=100, null=True, blank=True)
    api_path = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.api_path if self.api_path else "No API Path"

    class Meta:
        verbose_name = "Https"
        verbose_name_plural = "Https"

class Setting(models.Model):
    enable_printing = models.BooleanField(default=False)

    def __str__(self):
        return "Printing Enabled" if self.enable_printing else "Printing Disabled"

    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            raise ValueError("Only one instance of Setting is allowed.")
        super().save(*args, **kwargs)
