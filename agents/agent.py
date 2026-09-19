# agents/agents.py
import os
import sys
import time
import socket
import platform
import psutil
import requests
import json

# Conditional Windows Imports - Prevents Linux/macOS crashes
if platform.system().lower() == 'windows':
    try:
        import wmi
    except ImportError:
        wmi = None
else:
    wmi = None

# =========================================================================
# 🔀 CODESPACE GATEWAY ROUTE TUNING
# =========================================================================
# FIXED: Added the explicit '/api/ingest/' subpath endpoint onto your forwarding token address!
CENTRAL_API_URL = "https://127.0.0"
POLL_INTERVAL = 1800  # Restored standard 30 Minutes window to avoid DDoS self-locking
# =========================================================================

def get_os_platform():
    sys_platform = platform.system().lower()
    return 'macos' if sys_platform == 'darwin' else sys_platform

def determine_role(platform_str):
    hostname = socket.gethostname().lower()
    if platform_str == 'linux' or 'server' in hostname or psutil.cpu_count(logical=True) > 16:
        return 'server'
    return 'laptop'

def read_thermal_metrics(platform_str):
    """Interrogates host internal hardware sensors dynamically according to OS limits."""
    if platform_str == 'linux':
        try:
            temps = psutil.sensors_temperatures()
            for zone in ['coretemp', 'cpu_thermal', 'acpitz']:
                if zone in temps and temps[zone]:
                    return float(temps[zone][0].current)
            if temps:
                # Safe array indexing extraction fallback logic
                first_sensor_group = list(temps.values())[0]
                if first_sensor_group:
                    return float(first_sensor_group[0].current)
        except Exception:
            pass
            
    elif platform_str == 'windows' and wmi is not None:
        try:
            # Relies on active open background processing structures like LibreHardwareMonitor
            w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            for sensor in w.Sensor():
                if sensor.SensorType == 'Temperature' and 'cpu' in sensor.Name.lower():
                    return float(sensor.Value)
        except Exception:
            pass
            
    return -1.0

def inspect_active_directory():
    """Tracks status profiles for Windows Active Directory domain controller roles."""
    if platform.system().lower() != 'windows':
        return {}, False
        
    ad_services = ['NTDS', 'Kdc', 'LanmanWorkstation']
    service_matrix = {}
    is_dc = False
    
    for service in ad_services:
        try:
            status = psutil.win_service_get(service).status()
            service_matrix[service] = status
            if service in ['NTDS', 'Kdc'] and status == 'running':
                is_dc = True
        except Exception:
            service_matrix[service] = "Absent"
            
    return service_matrix, is_dc

def process_and_transmit():
    current_platform = get_os_platform()
    role = determine_role(current_platform)
    ram = psutil.virtual_memory()
    
    # Normalise file systems configuration paths
    root_path = 'C:\\' if current_platform == 'windows' else '/'
    try:
        disk = psutil.disk_usage(root_path)
        disk_used, disk_total = disk.percent, round(disk.total / (1024**3), 2)
    except Exception:
        disk_used, disk_total = -1.0, 0.0

    ad_matrix, is_dc = inspect_active_directory()
    
    # Structure metadata payload space configurations
    context = {"ad_services": ad_matrix}
    if psutil.sensors_battery():
        context["battery_pct"] = psutil.sensors_battery().percent
        context["on_ac_power"] = psutil.sensors_battery().power_plugged

    payload = {
        "hostname": socket.gethostname(),
        "device_role": role,
        "platform": current_platform,
        "ip_address": socket.gethostbyname(socket.gethostname()),
        
        # Static Parameters Profile
        "cpu_model": platform.processor() or "Generic Processor Core",
        "total_ram_gb": round(ram.total / (1024**3), 2),
        "total_disk_gb": disk_total,
        "is_active_directory": is_dc,
        
        # Telemetry Utilization Snapshot
        "cpu_usage_pct": psutil.cpu_percent(interval=1),
        "ram_usage_pct": ram.percent,
        "disk_usage_pct": disk_used,
        "cpu_temp_celsius": read_thermal_metrics(current_platform),
        "contextual_payload": context
    }
    return payload

#     # =========================================================================
#     # 📺 NEW: SHOW THE COLLECTED DATA IN THE TERMINAL INSTANTLY
#     # =========================================================================
#     print("\n" + "🔍" + "="*53)
#     print(f" 📊 AGENT SNAPSHOT COLLECTED AT: {time.strftime('%X')}")
#     print("="*55)
#     print(json.dumps(payload, indent=4))
#     print("="*55 + "\n")
#     # =========================================================================

#     try:
#         response = requests.post(CENTRAL_API_URL, json=payload, timeout=15)
#         print(f"[{time.strftime('%X')}] Synced fleet payload to gateway. Response code: {response.status_code}")
#     except Exception as err:
#         print(f"[{time.strftime('%X')}] Transmission pipeline failure: {err}")

# if __name__ == "__main__":
#     print(f"Initializing Multi-Platform Monitoring Agent ({platform.system()} Platform)...")
#     process_and_transmit()
#     while True:
#         time.sleep(POLL_INTERVAL)
#         process_and_transmit()
