from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import TargetDevice, TelemetryLog
from agents.agent import process_and_transmit

def index(request):
    payload=process_and_transmit()  # Trigger the background agent processing routine
    return render (request,'index.html','payload'=payload)
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
