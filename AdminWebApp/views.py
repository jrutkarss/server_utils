from django.shortcuts import render
from MainWebApp.models import TargetDevice, TelemetryLog

def dashboard_home(request):
    devices = TargetDevice.objects.all()
    devices_data = []

    for device in devices:
        # Query the log table directly for the newest entry belonging to this specific device
        latest_log = TelemetryLog.objects.filter(device=device).order_by('-timestamp').first()
        
        devices_data.append({
            'info': device,
            'metrics': latest_log
        })

    # Note: verify that the folder structure name is accurate inside your project layout
    return render(request, 'dashboard.html', {'devices_data': devices_data})
