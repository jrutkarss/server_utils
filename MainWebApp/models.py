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


class NetworkDevice(models.Model):
    """Represents a device discovered on the network switch"""
    ip_address = models.GenericIPAddressField(unique=True, db_index=True)
    mac_address = models.CharField(max_length=17, unique=True, db_index=True)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)  # router, printer, computer
    vendor = models.CharField(max_length=255, blank=True, null=True)
    online = models.BooleanField(default=True)
    
    # Timestamps
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['online', 'last_seen']),
        ]

    def __str__(self):
        return f"{self.hostname or self.ip_address} ({self.mac_address})"


class NetworkMetrics(models.Model):
    """Network performance metrics for discovered devices"""
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE, related_name='metrics')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Performance metrics (-1.0 = unavailable)
    cpu_usage_pct = models.FloatField(default=-1.0)
    memory_usage_pct = models.FloatField(default=-1.0)
    disk_usage_pct = models.FloatField(default=-1.0)
    network_in_mbps = models.FloatField(default=-1.0)
    network_out_mbps = models.FloatField(default=-1.0)
    ping_ms = models.FloatField(default=-1.0)
    
    # Additional context
    contextual_payload = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['device', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.device.hostname or self.device.ip_address} -- {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

