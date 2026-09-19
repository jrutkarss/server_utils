from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import TargetDevice, TelemetryLog, NetworkDevice, NetworkMetrics
from agents.agent import process_and_transmit

def index(request):
    payload = process_and_transmit()
    return render(request, 'index.html', {'payload': payload})

@csrf_exempt
def ingest_telemetry(request):
    """Receives JSON metric structures from cross-platform background agents."""
    if request.method != 'POST':
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
        
    try:
        data = json.loads(request.body)
        
        # Thread-safe atomic operational layout
        with transaction.atomic():
            # 1. Automatic machine provision discovery check-in routine
            device, created = TargetDevice.objects.update_or_create(
                hostname=data.get('hostname'),
                defaults={
                    'device_role': data.get('device_role', 'laptop'),
                    'platform': data.get('platform'),
                    'ip_address': data.get('ip_address'),
                    'cpu_model': data.get('cpu_model'),
                    'total_ram_gb': float(data.get('total_ram_gb', 0.0)),
                    'total_disk_gb': float(data.get('total_disk_gb', 0.0)),
                    'is_active_directory': data.get('is_active_directory', False)
                }
            )
            
            # 2. Append metrics to the historical database pipeline
            TelemetryLog.objects.create(
                device=device,
                cpu_usage_pct=float(data.get('cpu_usage_pct', -1.0)),
                ram_usage_pct=float(data.get('ram_usage_pct', -1.0)),
                disk_usage_pct=float(data.get('disk_usage_pct', -1.0)),
                cpu_temp_celsius=float(data.get('cpu_temp_celsius', -1.0)),
                contextual_payload=data.get('contextual_payload', {})
            )
            
        return JsonResponse({"status": "success", "message": f"Metrics stored for {device.hostname}"}, status=201)
        
    except (ValueError, TypeError, KeyError) as e:
        return JsonResponse({"error": f"Invalid payload structure: {str(e)}"}, status=400)


@csrf_exempt
def discover_network_devices(request):
    """Receives discovered devices from network scanning agent"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        devices_data = data.get('devices', [])
        
        with transaction.atomic():
            for device_info in devices_data:
                device, created = NetworkDevice.objects.update_or_create(
                    ip_address=device_info.get('ip_address'),
                    defaults={
                        'mac_address': device_info.get('mac_address', 'unknown'),
                        'hostname': device_info.get('hostname'),
                        'device_type': device_info.get('device_type'),
                        'vendor': device_info.get('vendor'),
                        'online': device_info.get('online', True)
                    }
                )
        
        return JsonResponse(
            {"status": "success", "message": f"Discovered {len(devices_data)} devices"},
            status=201
        )
    except (ValueError, TypeError, KeyError) as e:
        return JsonResponse({"error": f"Invalid payload: {str(e)}"}, status=400)


@csrf_exempt
def ingest_network_metrics(request):
    """Receives performance metrics from network scanning agent"""
    if request.method != 'POST':
        return JsonResponse({"error": "Method Not Allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        metrics_data = data.get('metrics', [])
        
        with transaction.atomic():
            for metric_info in metrics_data:
                try:
                    device = NetworkDevice.objects.get(ip_address=metric_info.get('ip_address'))
                    NetworkMetrics.objects.create(
                        device=device,
                        cpu_usage_pct=float(metric_info.get('cpu_usage_pct', -1.0)),
                        memory_usage_pct=float(metric_info.get('memory_usage_pct', -1.0)),
                        disk_usage_pct=float(metric_info.get('disk_usage_pct', -1.0)),
                        network_in_mbps=float(metric_info.get('network_in_mbps', -1.0)),
                        network_out_mbps=float(metric_info.get('network_out_mbps', -1.0)),
                        ping_ms=float(metric_info.get('ping_ms', -1.0)),
                        contextual_payload=metric_info.get('contextual_payload', {})
                    )
                except NetworkDevice.DoesNotExist:
                    continue
        
        return JsonResponse(
            {"status": "success", "message": f"Stored metrics for {len(metrics_data)} devices"},
            status=201
        )
    except (ValueError, TypeError, KeyError) as e:
        return JsonResponse({"error": f"Invalid payload: {str(e)}"}, status=400)


def get_network_devices(request):
    """Retrieve all discovered network devices"""
    devices = NetworkDevice.objects.all().select_related()
    devices_data = []
    
    for device in devices:
        latest_metric = NetworkMetrics.objects.filter(device=device).order_by('-timestamp').first()
        devices_data.append({
            'device': {
                'ip': device.ip_address,
                'mac': device.mac_address,
                'hostname': device.hostname,
                'online': device.online,
                'type': device.device_type,
                'last_seen': device.last_seen.isoformat()
            },
            'metrics': {
                'ping_ms': latest_metric.ping_ms if latest_metric else -1.0,
                'cpu_pct': latest_metric.cpu_usage_pct if latest_metric else -1.0,
                'memory_pct': latest_metric.memory_usage_pct if latest_metric else -1.0,
                'timestamp': latest_metric.timestamp.isoformat() if latest_metric else None
            } if latest_metric else None
        })
    
    return JsonResponse({'devices': devices_data}, status=200)

