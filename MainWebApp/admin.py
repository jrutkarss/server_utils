from django.contrib import admin

# Register your models here.
# MainWebApp/admin.py
from django.contrib import admin
from .models import TargetDevice, TelemetryLog

@admin.register(TargetDevice)
class TargetDeviceAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'platform', 'device_role', 'ip_address', 'last_seen')
    list_filter = ('platform', 'device_role')
    search_fields = ('hostname', 'ip_address')

@admin.register(TelemetryLog)
class TelemetryLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'timestamp', 'cpu_usage_pct', 'ram_usage_pct', 'disk_usage_pct', 'cpu_temp_celsius')
    list_filter = ('device__hostname', 'timestamp')
    date_hierarchy = 'timestamp'
