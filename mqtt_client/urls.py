from rest_framework.routers import DefaultRouter
from django.urls import path,include
from .views import (
    MqttSettingsViewSet,
    LogDataViewSet,
    DeviceDetailsViewSet,
    MachineDetailsViewSet,
    DeviceDataViewSet,
    MachineDataViewSet,
    ProductionDataViewSet,
    ShiftTimingViewSet
)

router = DefaultRouter()
router.register(r'mqtt-settings', MqttSettingsViewSet)
router.register(r'log-data', LogDataViewSet)
router.register(r'device-details', DeviceDetailsViewSet)
router.register(r'machine-details', MachineDetailsViewSet)
router.register(r'device-data', DeviceDataViewSet)
router.register(r'machine-data', MachineDataViewSet)
router.register(r'production-data', ProductionDataViewSet)
router.register(r'shift-timing', ShiftTimingViewSet)

urlpatterns = [
     path('',include(router.urls))
]
