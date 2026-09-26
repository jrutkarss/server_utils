# Server Utils - Multi-Platform System & Network Monitoring

[![Django CI](https://github.com/jrutkarss/server_utils/actions/workflows/django.yml/badge.svg)](https://github.com/jrutkarss/server_utils/actions/workflows/django.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.1+](https://img.shields.io/badge/django-6.1+-darkgreen.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

> **Comprehensive system and network monitoring platform** - Monitor local machine performance and discover/track all devices connected to your network switch.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Agents](#agents)
  - [Local System Agent](#local-system-agent)
  - [Network Machine Agent](#network-machine-agent)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Database Models](#database-models)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## Overview

**Server Utils** is a Django-based platform that provides real-time monitoring of:

1. **Local Machine Performance** - CPU, RAM, disk, temperature, and battery status
2. **Network Devices** - Automatic discovery and continuous monitoring of all devices on your network
3. **Centralized Dashboard** - Web interface to view all monitored devices and metrics

Perfect for:
- 🏢 Network administrators managing multiple devices
- 🔧 IT teams monitoring system health across infrastructure
- 📊 DevOps engineers tracking resource utilization
- 🎯 Anyone needing visibility into connected network devices

---

## Features

### 🖥️ Local System Monitoring
- **Cross-platform support** (Windows, Linux, macOS)
- **Real-time metrics**: CPU %, RAM %, disk %, GPU temperature
- **Hardware inventory**: CPU model, total RAM, total disk, device role classification
- **Active Directory detection** (Windows servers)
- **Battery monitoring** (laptops/mobile devices)
- **Automatic check-ins** every 30 minutes

### 🌐 Network Device Discovery & Monitoring
- **ARP scanning** - Discover all devices on configured subnet
- **Hostname resolution** - Reverse DNS lookups for device identification
- **Connectivity testing** - Ping-based availability detection with latency measurement
- **SNMP metrics** - Retrieve CPU and memory from SNMP-enabled devices
- **Multi-protocol support** - Works with routers, switches, printers, computers, etc.
- **Online/offline tracking** - Continuous status monitoring

### 🔐 Security & Reliability
- **Atomic transactions** - Data consistency guaranteed
- **Environment-based configuration** - No hardcoded secrets
- **CSRF protection** - Secure API endpoints
- **Flexible error handling** - Graceful degradation when metrics unavailable
- **Django admin interface** - Built-in admin panel for device management

### 📊 Data & Analytics
- **Time-series storage** - Historical metrics for trend analysis
- **Composite indexing** - Optimized database queries
- **RESTful API** - Programmatic access to all data
- **JSON payloads** - Flexible, extensible data format

---

## Quick Start

### 1️⃣ Clone & Install

```bash
git clone https://github.com/jrutkarss/server_utils.git
cd server_utils
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

```bash
# Create .env file
cat > .env << EOF
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CENTRAL_API_URL=http://localhost:8000/api/
NETWORK_GATEWAY=192.168.1.1
NETWORK_SUBNET=192.168.1.0/24
SNMP_COMMUNITY=public
POLL_INTERVAL=1800
EOF
```

### 3️⃣ Setup Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4️⃣ Run Server

```bash
python manage.py runserver
# Visit http://localhost:8000
```

### 5️⃣ Start Monitoring Agents

**Terminal 1 - Local System Agent:**
```bash
python agents/agent.py
```

**Terminal 2 - Network Device Agent:**
```bash
python agents/network_agent.py
```

> 📊 Both agents will start reporting data to http://localhost:8000/api/

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           SERVER UTILS MONITORING PLATFORM              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────────┐  │
│  │  Local Machine  │         │   Network Scanner    │  │
│  │  (agent.py)     │         │  (network_agent.py)  │  │
│  │                 │         │                      │  │
│  │ • CPU Usage     │         │ • ARP Scan           │  │
│  │ • RAM Usage     │         │ • Ping Devices       │  │
│  │ • Disk Usage    │         │ • SNMP Queries       │  │
│  │ • Temperature   │         │ • Resolve Hostnames  │  │
│  │ • Battery       │         │ • Track Online/Off   │  │
│  └────────┬────────┘         └──────────┬───────────┘  │
│           │                             │               │
│           └──────────────┬──────────────┘               │
│                          │                              │
│                   Django REST API                       │
│              /api/ingest/    /api/network-devices/*     │
│                          │                              │
│           ┌──────────────┼──────────────┐               │
│           │              │              │               │
│      TargetDevice   NetworkDevice   TelemetryLog        │
│      TelemetryLog   NetworkMetrics  (Database)          │
│                                                         │
│           ┌──────────────┴──────────────┐               │
│           │                             │               │
│        Admin Panel              Dashboard/API           │
│     (/admin/)                  (/api/network-devices/)  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Agents

### Local System Agent

**File:** `agents/agent.py`

Monitors the local machine and reports metrics every 30 minutes.

**What it measures:**
- CPU usage percentage
- RAM usage percentage & total capacity
- Disk usage percentage & total capacity
- CPU temperature (from hardware sensors)
- Device role (laptop vs. server)
- Platform (Windows, Linux, macOS)
- Active Directory status (Windows only)
- Battery level & AC power status (laptops only)

**Example output:**
```json
{
  "hostname": "workstation-01",
  "device_role": "laptop",
  "platform": "windows",
  "ip_address": "192.168.1.100",
  "cpu_model": "Intel Core i7-10700K",
  "total_ram_gb": 32.0,
  "total_disk_gb": 476.0,
  "cpu_usage_pct": 28.5,
  "ram_usage_pct": 62.3,
  "disk_usage_pct": 45.2,
  "cpu_temp_celsius": 52.1,
  "is_active_directory": false,
  "contextual_payload": {
    "battery_pct": 85.0,
    "on_ac_power": true,
    "ad_services": {}
  }
}
```

**Run it:**
```bash
python agents/agent.py
```

---

### Network Machine Agent

**File:** `agents/network_agent.py`

Discovers and monitors all devices connected to your network switch.

**What it does:**
1. Scans the network using ARP protocol to find all connected devices
2. Resolves hostnames via reverse DNS lookup
3. Tests connectivity via ping (latency & availability)
4. Queries SNMP-enabled devices for CPU and memory metrics
5. Reports all discoveries and metrics to the central API

**Supported device types:**
- Computers (desktops, laptops)
- Servers
- Network routers & switches
- Printers
- IoT devices
- Mobile devices (if accessible via network)

**Example discovery output:**
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
    },
    {
      "ip_address": "192.168.1.1",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "hostname": "gateway",
      "device_type": "router",
      "online": true
    }
  ],
  "timestamp": "2024-01-15T10:30:00",
  "scan_type": "arp"
}
```

**Run it:**
```bash
export NETWORK_GATEWAY=192.168.1.1
export NETWORK_SUBNET=192.168.1.0/24
python agents/network_agent.py
```

For detailed setup, see [NETWORK_AGENT_GUIDE.md](./NETWORK_AGENT_GUIDE.md).

---

## Installation

### Prerequisites

- **Python 3.9+**
- **pip** or **conda**
- **Git**
- Network access (for agent communications)
- Admin/root privileges (for some network scanning on certain platforms)

### Step-by-Step

#### 1. Clone Repository
```bash
git clone https://github.com/jrutkarss/server_utils.git
cd server_utils
```

#### 2. Create Virtual Environment
```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `Django>=6.1.1` - Web framework
- `requests>=2.31.0` - HTTP client for agent communications
- `psutil>=5.9.8` - System metrics collection
- `pysnmp>=4.4.12` - SNMP protocol support
- `scapy>=2.5.0` - Network packet tools
- `netaddr>=0.10.1` - IP address utilities
- `psycopg2-binary>=2.9.9` - PostgreSQL support (optional)
- `msal>=1.26.0` - Azure authentication (optional)

#### 4. Initialize Database
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5. Create Admin User
```bash
python manage.py createsuperuser
```

---

## Configuration

### Environment Variables

Create a `.env` file or export these variables:

```bash
# Django Settings
DJANGO_SECRET_KEY=your-very-secure-random-string-here
DEBUG=False                                    # True for development only
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# API Configuration
CENTRAL_API_URL=http://localhost:8000/api/   # Where agents report to

# Network Scanning
NETWORK_GATEWAY=192.168.1.1                  # Your network gateway/router IP
NETWORK_SUBNET=192.168.1.0/24                # Subnet to scan (CIDR notation)
SNMP_COMMUNITY=public                        # SNMP community string

# Polling Intervals (seconds)
POLL_INTERVAL=1800                           # 30 minutes between scans
```

### Django Settings

Edit `server_utils/settings.py` for advanced configuration:

```python
# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'MainWebApp',              # Main monitoring app
    'AdminWebApp',             # Admin interface
]

# Database (default: SQLite)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# For production, use PostgreSQL:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'server_utils'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

---

## Usage

### Starting the Server

**Development:**
```bash
python manage.py runserver
```
Access at `http://localhost:8000`

**Production:**
```bash
gunicorn server_utils.wsgi:application --bind 0.0.0.0:8000
```

### Starting Agents

**Option 1: Manual (Development)**
```bash
# Terminal 1
python agents/agent.py

# Terminal 2
python agents/network_agent.py
```

**Option 2: Systemd Service (Linux)**

Create `/etc/systemd/system/server-utils-agent.service`:
```ini
[Unit]
Description=Server Utils Monitoring Agents
After=network.target

[Service]
Type=forking
User=your_user
WorkingDirectory=/path/to/server_utils
ExecStart=/path/to/venv/bin/python agents/agent.py
ExecStart=/path/to/venv/bin/python agents/network_agent.py
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

Start:
```bash
sudo systemctl enable server-utils-agent
sudo systemctl start server-utils-agent
sudo systemctl status server-utils-agent
```

**Option 3: Windows Task Scheduler**

See [NETWORK_AGENT_GUIDE.md](./NETWORK_AGENT_GUIDE.md#option-3-windows-task-scheduler) for detailed instructions.

### Accessing the Dashboard

1. **Admin Panel**: http://localhost:8000/admin/
   - View all devices
   - Edit device information
   - Delete old entries

2. **API Endpoints**: http://localhost:8000/api/
   - Get device list
   - Query metrics
   - Programmatic access

### Common Tasks

**View all local machines:**
```bash
curl http://localhost:8000/api/ingest/
```

**View all network devices:**
```bash
curl http://localhost:8000/api/network-devices/
```

**View device metrics:**
```bash
curl "http://localhost:8000/api/network-devices/?device=192.168.1.100"
```

---

## API Reference

### Local Machine Metrics

**POST** `/api/ingest/`

Report local machine metrics.

```json
{
  "hostname": "workstation-01",
  "platform": "windows",
  "device_role": "laptop",
  "ip_address": "192.168.1.100",
  "cpu_usage_pct": 35.2,
  "ram_usage_pct": 62.1,
  "disk_usage_pct": 48.5,
  "cpu_temp_celsius": 52.3
}
```

Response: `201 Created`

### Network Devices

**GET** `/api/network-devices/`

Retrieve all discovered network devices with latest metrics.

Response:
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

**POST** `/api/network-devices/discover/`

Report discovered devices (used by network agent).

**POST** `/api/network-devices/metrics/`

Report network metrics (used by network agent).

See [API documentation](./NETWORK_AGENT_GUIDE.md#api-endpoints) for complete details.

---

## Database Models

### TargetDevice
Stores static information about local machines reporting metrics.

```python
hostname (CharField)           # Machine name (unique)
device_role (CharField)        # "server" or "laptop"
platform (CharField)           # "windows", "linux", "macos"
ip_address (GenericIPAddressField)  # IPv4 or IPv6
cpu_model (CharField)          # CPU identifier
total_ram_gb (FloatField)      # Total RAM capacity
total_disk_gb (FloatField)     # Total disk capacity
is_active_directory (BooleanField)  # Active Directory domain member
last_seen (DateTimeField)      # Last update timestamp
created_at (DateTimeField)     # First recorded timestamp
```

### TelemetryLog
Time-series metrics for local machines.

```python
device (ForeignKey → TargetDevice)
timestamp (DateTimeField)
cpu_usage_pct (FloatField)
ram_usage_pct (FloatField)
disk_usage_pct (FloatField)
cpu_temp_celsius (FloatField)
contextual_payload (JSONField)  # Extra data (battery, AD services, etc)
```

### NetworkDevice
Discovered network-connected devices.

```python
ip_address (GenericIPAddressField)  # Unique, indexed
mac_address (CharField)              # Unique, indexed
hostname (CharField)                 # Reverse DNS name
device_type (CharField)              # "router", "printer", "computer"
vendor (CharField)                   # Manufacturer
online (BooleanField)                # Availability
first_seen (DateTimeField)
last_seen (DateTimeField)
```

### NetworkMetrics
Performance metrics for network devices.

```python
device (ForeignKey → NetworkDevice)
timestamp (DateTimeField)
cpu_usage_pct (FloatField)
memory_usage_pct (FloatField)
disk_usage_pct (FloatField)
network_in_mbps (FloatField)
network_out_mbps (FloatField)
ping_ms (FloatField)
contextual_payload (JSONField)
```

---

## Troubleshooting

### Agent not starting

**Error:** `ModuleNotFoundError: No module named 'psutil'`

**Solution:**
```bash
pip install -r requirements.txt
```

**Error:** `Connection refused` when reporting to API

**Solution:**
- Ensure Django server is running: `python manage.py runserver`
- Check `CENTRAL_API_URL` environment variable
- Verify network connectivity: `ping localhost`

### Network scanning not finding devices

**Symptom:** No devices discovered after running network agent

**Solutions:**
- Verify gateway IP: `ping 192.168.1.1` (adjust to your network)
- Check subnet configuration: Ensure `NETWORK_SUBNET` matches your actual network
- Run with elevated privileges (may be required for ARP scanning)
- On Windows: Disable firewall temporarily for testing

### Database errors

**Error:** `django.db.utils.OperationalError: no such table`

**Solution:**
```bash
python manage.py migrate
```

**Error:** `django.core.exceptions.ImproperlyConfigured`

**Solution:**
- Verify `DJANGO_SECRET_KEY` is set
- Check all required environment variables
- Ensure `settings.py` is properly configured

### SNMP queries failing

**Symptom:** SNMP metrics always show -1.0

**Solutions:**
- Install SNMP library: `pip install pysnmp`
- Verify SNMP is enabled on target device
- Check community string: `export SNMP_COMMUNITY="public"`
- Ensure firewall allows SNMP (UDP port 161)

---

## Project Structure

```
server_utils/
├── server_utils/          # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py           # URL routing
│   ├── wsgi.py           # WSGI application
│   └── asgi.py           # ASGI application
│
├── MainWebApp/           # Main monitoring application
│   ├── models.py         # TargetDevice, TelemetryLog, NetworkDevice, NetworkMetrics
│   ├── views.py          # API endpoints
│   ├── urls.py           # URL patterns
│   ├── admin.py          # Admin interface
│   └── templates/        # HTML templates
│
├── AdminWebApp/          # Admin application
│   ├── views.py          # Dashboard views
│   └── templates/        # Dashboard templates
│
├── agents/               # Monitoring agents
│   ├── agent.py          # Local system monitoring
│   └── network_agent.py   # Network device discovery
│
├── manage.py             # Django management
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── NETWORK_AGENT_GUIDE.md    # Detailed network agent documentation
├── IMPLEMENTATION_SUMMARY.md # Technical implementation details
└── LICENSE               # MIT License
```

---

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

Follow PEP 8:
```bash
pip install flake8
flake8 .
```

### Local Development Setup

```bash
# Create .env.local
cp .env.example .env.local

# Edit with local settings
# DEBUG=True
# DJANGO_SECRET_KEY=dev-key-for-local-only
# ALLOWED_HOSTS=localhost,127.0.0.1

# Install dev dependencies
pip install -r requirements-dev.txt

# Run with hot reload
python manage.py runserver
```

---

## Performance Tuning

### Database Optimization

Use PostgreSQL for production instead of SQLite:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'server_utils',
        'HOST': 'db-server',
    }
}
```

### Agent Tuning

Adjust polling intervals based on your needs:
```bash
# Faster monitoring (every 5 minutes)
export POLL_INTERVAL=300

# Slower monitoring (every 2 hours)
export POLL_INTERVAL=7200
```

### Network Scanning Optimization

Reduce scope for faster scans:
```bash
# Scan smaller subnet
export NETWORK_SUBNET=192.168.1.0/25

# Or disable SNMP queries
export SNMP_COMMUNITY=""
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see [LICENSE](./LICENSE) file for details.

---

## Support & Issues

- 📖 See [NETWORK_AGENT_GUIDE.md](./NETWORK_AGENT_GUIDE.md) for detailed setup help
- 📋 See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for technical details
- 🐛 Create an issue on GitHub for bugs or feature requests
- 💬 Discuss ideas in GitHub Discussions

---

## Acknowledgments

- Built with [Django](https://www.djangoproject.com/)
- System metrics via [psutil](https://github.com/giampaolo/psutil)
- Network scanning via [ARP](https://en.wikipedia.org/wiki/Address_Resolution_Protocol) and [SNMP](https://en.wikipedia.org/wiki/Simple_Network_Management_Protocol)
- Community contributions and feedback

---

**Last Updated:** September 2026
**Version:** 1.0.0
