from django.contrib import admin
from .models import LogData, DeviceData, ProductionData, MachineData, DeviceDetails, MachineDetails, MqttSettings, HttpsSettings,Setting

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
    list_display = ('device_name', 'device_token', 'hardware_version', 'software_version', 'protocol')

@admin.register(MachineDetails)
class MachineDetailsAdmin(admin.ModelAdmin):
    list_display = ('machine_id', 'machine_name')

class MqttSettingsAdmin(admin.ModelAdmin):
    list_display = ('server_name_alias', 'host', 'port', 'username', 'qos','keepalive')
    search_fields = ('server_name_alias', 'host', 'username')

class HttpsSettingsAdmin(admin.ModelAdmin):
    list_display = ('api_path', 'auth_token')
    search_fields = ('api_path',)

class SettingAdmin(admin.ModelAdmin):
    list_display = ('id', 'enable_printing')
    def has_add_permission(self, request) :
        if Setting.objects.count() > 0:
            return False
        return True

admin.site.register(MqttSettings, MqttSettingsAdmin)
admin.site.register(HttpsSettings, HttpsSettingsAdmin)
admin.site.register(Setting, SettingAdmin)
