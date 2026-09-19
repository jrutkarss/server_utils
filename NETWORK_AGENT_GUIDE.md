# Network Machine Usage Agent - Setup & Usage Guide

## Overview

The **Network Machine Usage Agent** monitors devices connected to your network switch by their IP address. It performs network discovery, collects performance metrics, and reports them to the central Django API.

## Features

✅ **Network Discovery** - Scans network using ARP to find all connected devices  
✅ **Device Identification** - Performs reverse DNS lookups to resolve hostnames  
✅ **Ping Monitoring** - Checks device availability and latency  
✅ **SNMP Queries** - Retrieves CPU/memory metrics from SNMP-enabled devices  
✅ **Centralized Reporting** - Sends all data to Django API endpoints  
✅ **Cross-Platform** - Works on Windows, Linux, and macOS  

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `pysnmp>=4.4.12` - SNMP protocol support
- `python-nmap>=0.0.1` - Network scanning
- `scapy>=2.5.0` - Packet manipulation
- `netaddr>=0.10.1` - IP address utilities

### 2. Configuration

Set environment variables:

```bash
# API Endpoint
export CENTRAL_API_URL="http://localhost:8000/api/"

# Network Configuration
export NETWORK_GATEWAY="192.168.1.1"
export NETWORK_SUBNET="192.168.1.0/24"
export SNMP_COMMUNITY="public"

# Polling Interval (seconds)
export POLL_INTERVAL="1800"  # 30 minutes
```

On Windows (PowerShell):
```powershell
$env:CENTRAL_API_URL = "http://localhost:8000/api/"
$env:NETWORK_GATEWAY = "192.168.1.1"
$env:NETWORK_SUBNET = "192.168.1.0/24"
```

### 3. Database Migrations

The new network models need to be migrated:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates two new tables:
- **NetworkDevice** - Stores discovered devices (IP, MAC, hostname, online status)
- **NetworkMetrics** - Stores performance metrics per device (CPU, memory, ping, etc.)

## Running the Agent

### Option 1: Direct Execution

```bash
python agents/network_agent.py
```

This will start the agent and scan the network immediately, then repeat every 30 minutes.

### Option 2: Background Service (Linux/macOS)

Create a systemd service:

```bash
sudo nano /etc/systemd/system/network-agent.service
```

```ini
[Unit]
Description=Network Machine Usage Agent
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/server_utils
Environment="CENTRAL_API_URL=http://localhost:8000/api/"
Environment="NETWORK_GATEWAY=192.168.1.1"
ExecStart=/usr/bin/python3 agents/network_agent.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Start the service:
```bash
sudo systemctl enable network-agent
sudo systemctl start network-agent
sudo systemctl status network-agent
```

### Option 3: Windows Task Scheduler

1. Create a PowerShell script `start-network-agent.ps1`:
```powershell
cd C:\path\to\server_utils
$env:CENTRAL_API_URL = "http://localhost:8000/api/"
python agents/network_agent.py
```

2. Open Task Scheduler and create a new task:
   - Action: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\path\to\start-network-agent.ps1"`
   - Trigger: At startup or scheduled interval

## API Endpoints

### 1. Discover Network Devices

**POST** `/api/network-devices/discover/`

Request body:
```json
{
  "devices": [
    {
      "ip_address": "192.168.1.100",
      "mac_address": "00:1A:2B:3C:4D:5E",
      "hostname": "pc-01",
      "device_type": "computer",
      "vendor": "Dell",
      "online": true
    }
  ],
  "timestamp": "2024-01-15T10:30:00",
  "scan_type": "arp"
}
```

Response: `201 Created`
```json
{
  "status": "success",
  "message": "Discovered 5 devices"
}
```

### 2. Ingest Network Metrics

**POST** `/api/network-devices/metrics/`

Request body:
```json
{
  "metrics": [
    {
      "ip_address": "192.168.1.100",
      "device_name": "pc-01",
      "cpu_usage_pct": 45.2,
      "memory_usage_pct": 62.8,
      "disk_usage_pct": -1.0,
      "network_in_mbps": 12.5,
      "network_out_mbps": 8.3,
      "ping_ms": 2.1,
      "timestamp": "2024-01-15T10:30:00"
    }
  ]
}
```

Response: `201 Created`
```json
{
  "status": "success",
  "message": "Stored metrics for 5 devices"
}
```

### 3. Retrieve Network Devices

**GET** `/api/network-devices/`

Response: `200 OK`
```json
{
  "devices": [
    {
      "device": {
        "ip": "192.168.1.100",
        "mac": "00:1A:2B:3C:4D:5E",
        "hostname": "pc-01",
        "online": true,
        "type": "computer",
        "last_seen": "2024-01-15T10:30:00Z"
      },
      "metrics": {
        "ping_ms": 2.1,
        "cpu_pct": 45.2,
        "memory_pct": 62.8,
        "timestamp": "2024-01-15T10:30:00Z"
      }
    }
  ]
}
```

## Database Models

### NetworkDevice
```python
- ip_address (GenericIPAddressField) - unique, indexed
- mac_address (CharField) - unique, indexed
- hostname (CharField) - reverse DNS name
- device_type (CharField) - router, printer, computer, etc.
- vendor (CharField) - manufacturer info
- online (BooleanField) - current availability
- first_seen (DateTimeField) - auto_now_add
- last_seen (DateTimeField) - auto_now, indexed
```

### NetworkMetrics
```python
- device (ForeignKey) - link to NetworkDevice
- timestamp (DateTimeField) - auto_now_add, indexed
- cpu_usage_pct (FloatField) - -1.0 if unavailable
- memory_usage_pct (FloatField)
- disk_usage_pct (FloatField)
- network_in_mbps (FloatField)
- network_out_mbps (FloatField)
- ping_ms (FloatField)
- contextual_payload (JSONField) - flexible extra data
```

## Troubleshooting

### Agent not discovering devices
- Verify network connectivity: `ping 192.168.1.1`
- Check ARP cache: `arp -a` (Windows) or `arp -a` (Linux/macOS)
- Ensure sufficient permissions (may need admin on Windows)

### SNMP queries failing
- Install pysnmp: `pip install pysnmp`
- Verify SNMP is enabled on target device
- Check community string configuration: `export SNMP_COMMUNITY="public"`

### API connection errors
- Verify Django server is running: `python manage.py runserver`
- Check API URL: `export CENTRAL_API_URL="http://localhost:8000/api/"`
- Test connection: `curl -X GET http://localhost:8000/api/network-devices/`

### Permissions issues (Windows)
- Run as Administrator
- Disable Windows Firewall for local testing
- Check firewall rules for ARP traffic

## Performance Tuning

### Increase scan frequency
```bash
export POLL_INTERVAL="300"  # Scan every 5 minutes
```

### Reduce network scope
```bash
export NETWORK_SUBNET="192.168.1.0/25"  # Scan only first half of subnet
```

### Disable SNMP queries
Set `SNMP_COMMUNITY=""` to skip SNMP lookups and speed up scanning

## Security Considerations

⚠️ **SNMP Community String** - Default is "public", change in production:
```bash
export SNMP_COMMUNITY="your-secure-community-string"
```

⚠️ **API Authentication** - Add Django API authentication (tokens, OAuth2, etc.)

⚠️ **Network Access** - Restrict API access to trusted networks using Django settings

## Code Architecture

### NetworkScanner Class
- `arp_scan()` - Discover devices on network
- `resolve_hostname()` - Reverse DNS lookup
- `ping_device()` - Test device connectivity
- `snmp_query()` - Retrieve SNMP metrics
- `scan_and_collect_metrics()` - Main orchestration

### NetworkReporter Class
- `send_devices()` - POST to `/discover/` endpoint
- `send_metrics()` - POST to `/metrics/` endpoint

### Data Classes
- `NetworkDevice` - Discovered device representation
- `NetworkMetrics` - Performance metrics snapshot

## Example: Monitoring a Specific Subnet

```python
from agents.network_agent import NetworkScanner, NetworkReporter

scanner = NetworkScanner(
    gateway="10.0.0.1",
    subnet="10.0.0.0/24"
)

devices, metrics = scanner.scan_and_collect_metrics()
reporter = NetworkReporter()
reporter.send_devices(devices)
reporter.send_metrics(metrics)
```

## Integration with Main Agent

Both agents work together:

1. **Local Agent** (`agents/agent.py`) - Monitors local machine and sends to `/api/ingest/`
2. **Network Agent** (`agents/network_agent.py`) - Monitors network devices and sends to `/api/network-devices/*`

Both report to the same Django instance and can be cross-referenced via IP address.

## Dashboard Example Query

Get all devices and their latest metrics:
```python
from MainWebApp.models import NetworkDevice, NetworkMetrics

devices_with_metrics = []
for device in NetworkDevice.objects.filter(online=True):
    latest_metric = device.metrics.latest('timestamp')
    devices_with_metrics.append({
        'device': device,
        'metrics': latest_metric
    })
```

## License

Same as the main server_utils project.

## Support

For issues or questions, please refer to the main README.md or create a GitHub issue.
