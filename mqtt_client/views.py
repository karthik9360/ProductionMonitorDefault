from rest_framework import viewsets
from .models import MqttSettings, LogData, DeviceDetails, MachineDetails, DeviceData, MachineData, ProductionData, ShiftTiming
from .serializers import (
    MqttSettingsSerializer,
    LogDataSerializer,
    DeviceDetailsSerializer,
    MachineDetailsSerializer,
    DeviceDataSerializer,
    MachineDataSerializer,
    ProductionDataSerializer,
    ShiftTimingSerializer
)

class MqttSettingsViewSet(viewsets.ModelViewSet):
    queryset = MqttSettings.objects.all()
    serializer_class = MqttSettingsSerializer

class LogDataViewSet(viewsets.ModelViewSet):
    queryset = LogData.objects.all()
    serializer_class = LogDataSerializer

class DeviceDetailsViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetails.objects.all()
    serializer_class = DeviceDetailsSerializer

class MachineDetailsViewSet(viewsets.ModelViewSet):
    queryset = MachineDetails.objects.all()
    serializer_class = MachineDetailsSerializer

class DeviceDataViewSet(viewsets.ModelViewSet):
    queryset = DeviceData.objects.all()
    serializer_class = DeviceDataSerializer

class MachineDataViewSet(viewsets.ModelViewSet):
    queryset = MachineData.objects.all()
    serializer_class = MachineDataSerializer

class ProductionDataViewSet(viewsets.ModelViewSet):
    queryset = ProductionData.objects.all()
    serializer_class = ProductionDataSerializer

class ShiftTimingViewSet(viewsets.ModelViewSet):
    queryset = ShiftTiming.objects.all()
    serializer_class = ShiftTimingSerializer
