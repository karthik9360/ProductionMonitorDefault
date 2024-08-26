from rest_framework import serializers
from .models import MqttSettings, LogData, DeviceDetails, MachineDetails, DeviceData, MachineData, ProductionData, ShiftTiming, Setting, HttpsSettings

class MqttSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MqttSettings
        fields = '__all__'

class LogDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogData
        fields = '__all__'

class DeviceDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceDetails
        fields = '__all__'

class MachineDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineDetails
        fields = '__all__'

class DeviceDataSerializer(serializers.ModelSerializer):
    device_id = serializers.PrimaryKeyRelatedField(queryset=DeviceDetails.objects.all())
    log_data_id = serializers.PrimaryKeyRelatedField(queryset=LogData.objects.all())

    class Meta:
        model = DeviceData
        fields = '__all__'

class MachineDataSerializer(serializers.ModelSerializer):
    machine_id = serializers.PrimaryKeyRelatedField(queryset=MachineDetails.objects.all())
    device_id = serializers.PrimaryKeyRelatedField(queryset=DeviceDetails.objects.all())
    data_id = serializers.PrimaryKeyRelatedField(queryset=LogData.objects.all())

    class Meta:
        model = MachineData
        fields = '__all__'

class ProductionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionData
        fields = '__all__'

class ShiftTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShiftTiming
        fields = '__all__'


class HttpsSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = HttpsSettings
        fields = '__all__'

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ('__all__')