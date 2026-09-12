from django.db import models

# Create your models here.
from django.db import models

class TargetDevice(models.Model):
    """Stores the structural and static inventory spec profile of an asset."""
    PLATFORM_CHOICES = [
        ('windows', 'Windows'),
        ('linux', 'Linux'),
        ('macos', 'macOS'),
        ('ios', 'iOS'),
    ]
    
    DEVICE_ROLE = [
        ('server', 'Server'),
        ('laptop', 'Laptop'),
        ('mobile', 'Mobile / Tablet'),
    ]

    hostname = models.CharField(max_length=255, unique=True, db_index=True)
    device_role = models.CharField(max_length=20, choices=DEVICE_ROLE, default='laptop')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    # Static Hardware Inventories
    cpu_model = models.CharField(max_length=255, blank=True, null=True)
    total_ram_gb = models.FloatField(default=0.0)
    total_disk_gb = models.FloatField(default=0.0)
    
    # Flags & Timestamps
    is_active_directory = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.platform.upper()}] {self.hostname}"


class TelemetryLog(models.Model):
    """Tracks time-series usage metrics reported every 30 minutes."""
    device = models.ForeignKey(TargetDevice, on_delete=models.CASCADE, related_name='telemetry')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Dynamic resource percentages (-1.0 flags unavailable datasets)
    cpu_usage_pct = models.FloatField(default=-1.0)
    ram_usage_pct = models.FloatField(default=-1.0)
    disk_usage_pct = models.FloatField(default=-1.0)
    cpu_temp_celsius = models.FloatField(default=-1.0)
    
    # Flexible container for multi-platform varying metrics
    contextual_payload = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-timestamp']
        # Composite indexing accelerates chart time-filtering execution
        indexes = [
            models.Index(fields=['device', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.device.hostname} -- {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
