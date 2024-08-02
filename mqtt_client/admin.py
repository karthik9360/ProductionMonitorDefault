from django.contrib import admin
from .models import LogData, DeviceData, ProductionData, MachineData, DeviceDetails, MachineDetails

@admin.register(LogData)
class LogDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'received_data', 'protocol', 'topic_api', 'unique_id')

@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'time', 'data', 'device_id', 'protocol', 'topic_api', 'log_data_id')

@admin.register(ProductionData)
class ProductionDataAdmin(admin.ModelAdmin):
    list_display = ('machine_id', 'production_count', 'date', 'time')

@admin.register(MachineData)
class MachineDataAdmin(admin.ModelAdmin):
    list_display = ('machine_id', 'data', 'date', 'time')

@admin.register(DeviceDetails)
class DeviceDetailsAdmin(admin.ModelAdmin):
    list_display = ('device_token', 'sub_topic', 'pub_topic')

@admin.register(MachineDetails)
class MachineDetailsAdmin(admin.ModelAdmin):
    list_display = ('machine_id', 'machine_name')
